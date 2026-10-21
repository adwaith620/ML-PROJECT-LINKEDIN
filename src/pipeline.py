"""
pipeline.py

Unified Resume Screening & Skill Gap Analysis Pipeline.
Orchestrates:
1. File validation & text extraction (PDF, DOCX, TXT)
2. Text cleaning & normalization (preserving technical tokens)
3. Job Description section parsing (Required vs Preferred vs Contextual)
4. Multi-tier skill match classification (Exact, Alias, Related, Not Evidenced)
5. Non-fabricated, prioritized sentence evidence extraction (Work Experience > Projects > Skills)
6. Multi-modal similarity matching (TF-IDF Baseline + Sentence-BERT all-MiniLM-L6-v2)
7. Configurable weighted scoring with explicit component transparency
8. Publication-ready structured analysis result with quality warnings
"""

import os
import re
import uuid
import logging
from typing import Dict, Any, Optional, Tuple, List, Union

from src.resume_parser import (
    extract_document_text,
    DocumentParserError,
    FileSizeExceededError,
    PageLimitExceededError,
    TextLengthExceededError,
    UnsupportedFormatError,
    CorruptedDocumentError,
    EncryptedDocumentError,
    EmptyDocumentError,
)
from src.preprocessing.text_cleaner import clean_text
from src.skill_extraction.extractor import extract_from_resume
from src.skill_extraction.jd_parser import parse_job_description
from src.skill_extraction.match_classifier import classify_skill_matches
from src.scoring.candidate_score import calculate_candidate_score
from src.matching.sentence_bert import SemanticMatcher

logger = logging.getLogger(__name__)

# Singleton / cached models
_SEMANTIC_MATCHER: Optional[SemanticMatcher] = None
_BASELINE_EXTRACTOR = None
_BASELINE_LOADED = False


def get_semantic_matcher() -> SemanticMatcher:
    """Retrieve or initialize the cached SemanticMatcher instance."""
    global _SEMANTIC_MATCHER
    if _SEMANTIC_MATCHER is None:
        _SEMANTIC_MATCHER = SemanticMatcher(lazy=True)
    return _SEMANTIC_MATCHER


def get_baseline_feature_extractor():
    """Retrieve or load the pre-trained BaselineFeatureExtractor if available."""
    global _BASELINE_EXTRACTOR, _BASELINE_LOADED
    if not _BASELINE_LOADED:
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "baseline_feature_extractor.joblib")
        model_path = os.path.abspath(model_path)
        if os.path.exists(model_path):
            try:
                import joblib
                _BASELINE_EXTRACTOR = joblib.load(model_path)
                logger.info("Loaded pre-trained baseline_feature_extractor.joblib")
            except Exception as e:
                logger.warning(f"Could not load baseline feature extractor: {e}")
                _BASELINE_EXTRACTOR = None
        else:
            _BASELINE_EXTRACTOR = None
        _BASELINE_LOADED = True
    return _BASELINE_EXTRACTOR


def compute_baseline_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Computes TF-IDF cosine similarity between resume and job description.
    Uses pre-trained extractor if available, otherwise fits a pairwise vectorizer.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    extractor = get_baseline_feature_extractor()
    if extractor is not None and getattr(extractor, "is_fitted", False):
        try:
            df = extractor.transform([resume_text], [jd_text])
            sim = float(df['tfidf_cosine_similarity'].iloc[0])
            return max(0.0, min(1.0, sim))
        except Exception as e:
            logger.warning(f"Error using pre-trained baseline extractor: {e}")

    # Fallback to direct pairwise TF-IDF
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vec = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b\w+\b|[+#.]\w+')
        tfidf_mat = vec.fit_transform([resume_text, jd_text])
        sim = float(cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:2])[0][0])
        return max(0.0, min(1.0, sim))
    except Exception as e:
        logger.warning(f"Error in fallback TF-IDF computation: {e}")
        return 0.0


def analyze_candidate(
    resume_input: Union[bytes, str],
    resume_filename: str,
    jd_input: Union[bytes, str],
    jd_filename: Optional[str] = None,
    preferred_method: str = "auto",  # 'auto', 'semantic', 'classical'
) -> Dict[str, Any]:
    """
    End-to-end analysis of a candidate resume against a job description.
    
    Args:
        resume_input: Raw bytes or path to resume file.
        resume_filename: Name of the resume file.
        jd_input: Raw bytes, file path, or plain text of job description.
        jd_filename: Name of JD file if uploaded as a file, or None if pasted text.
        preferred_method: 'auto' (use semantic if available, fallback to classical),
                         'semantic' (strictly semantic),
                         'classical' (strictly TF-IDF).
                         
    Returns:
        Structured analysis report dictionary.
    """
    request_id = str(uuid.uuid4())
    warnings: List[str] = []

    # 1. Parse Resume Document
    raw_resume_text, resume_meta = extract_document_text(
        resume_input, filename=resume_filename, is_resume=True
    )

    # 2. Parse Job Description Document / Text
    if jd_filename:
        raw_jd_text, jd_meta = extract_document_text(
            jd_input, filename=jd_filename, is_resume=False
        )
    else:
        # JD was pasted as string
        if isinstance(jd_input, bytes):
            jd_str = jd_input.decode("utf-8", errors="replace")
        else:
            jd_str = str(jd_input)

        raw_jd_text = jd_str.strip()
        if not raw_jd_text:
            raise EmptyDocumentError("Job description cannot be empty. Please paste or upload a JD.")

        jd_meta = {
            "filename": "Pasted Job Description",
            "format": "text",
            "file_size_bytes": len(raw_jd_text.encode("utf-8")),
            "extracted_text_bytes": len(raw_jd_text.encode("utf-8")),
            "word_count": len(raw_jd_text.split()),
            "char_count": len(raw_jd_text),
            "unit_count": 1,
            "is_resume": False,
        }

    # 3. Clean Text while preserving technical tokens
    cleaned_resume = clean_text(raw_resume_text, lowercase=False)
    cleaned_jd = clean_text(raw_jd_text, lowercase=False)

    if len(cleaned_resume.split()) < 30:
        warnings.append("Resume contains very few words (< 30 words). Extraction confidence may be low.")
    if len(cleaned_jd.split()) < 20:
        warnings.append("Job description is very brief (< 20 words). Matching accuracy may be limited.")

    # 4. Job Description Section-Aware Skill Parsing
    jd_analysis = parse_job_description(cleaned_jd)
    required_skills = jd_analysis["required_skills"]
    preferred_skills = jd_analysis["preferred_skills"]
    contextual_skills = jd_analysis["contextual_skills"]
    section_certainty = jd_analysis["section_certainty"]
    detected_sections = jd_analysis["detected_sections"]

    if section_certainty == "inferred":
        warnings.append(
            "Job description does not contain explicit 'Required' vs 'Preferred' section headers. "
            "Skill requirements were inferred using contextual cues."
        )

    if not required_skills:
        warnings.append(
            "No explicit required technical skills were identified in the job description. "
            "Compatibility score relies predominantly on semantic and lexical alignment."
        )

    # 5. Extract Skills and Entities from Resume
    resume_entities = extract_from_resume(cleaned_resume)
    cand_skills_detailed = resume_entities.get("skills", [])

    if not cand_skills_detailed:
        warnings.append(
            "No technical skills from the standard taxonomy were detected in the candidate resume."
        )

    # 6. Detailed Multi-Tier Skill Match Classification & Evidence Extraction
    match_result = classify_skill_matches(
        resume_skills_dict=cand_skills_detailed,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        resume_text=raw_resume_text
    )

    matched_required = match_result["matched_required"]
    related_matches = match_result["related_matches"]
    missing_required = match_result["missing_required"]
    matched_preferred = match_result["matched_preferred"]
    missing_preferred = match_result["missing_preferred"]
    additional_skills = match_result["additional_skills"]
    metrics = match_result["metrics"]

    # 7. Similarities & Matching
    # Baseline TF-IDF
    baseline_similarity = compute_baseline_tfidf_similarity(cleaned_resume, cleaned_jd)

    # Semantic Sentence-BERT
    semantic_similarity: Optional[float] = None
    active_method = "Classical Baseline (TF-IDF)"

    matcher = get_semantic_matcher()
    can_use_semantic = (preferred_method in ("auto", "semantic"))

    if can_use_semantic:
        try:
            if matcher.load_model():
                raw_sem = matcher.compute_similarity(cleaned_resume, cleaned_jd)
                semantic_similarity = round(max(0.0, min(1.0, float(raw_sem))), 4)
                active_method = "Sentence-BERT (all-MiniLM-L6-v2) + Classical Hybrid"
            else:
                if preferred_method == "semantic":
                    raise RuntimeError(f"Sentence-BERT required but failed to load: {matcher._load_error}")
                warnings.append(
                    f"Sentence-BERT unavailable ({matcher._load_error or 'download error'}). "
                    "Used Classical TF-IDF matching fallback."
                )
        except Exception as e:
            logger.warning(f"Semantic matcher execution error: {e}")
            if preferred_method == "semantic":
                raise
            warnings.append(f"Semantic matcher encountered an error ({str(e)}). Used Classical fallback.")
            semantic_similarity = None

    # 8. Score Calculation
    # Preferred skills provide a modest, capped bonus (up to 5.0 pts, 2 pts per preferred skill matched)
    preferred_bonus = min(5.0, metrics["preferred_skills_matched_count"] * 2.0)

    score_data = calculate_candidate_score(
        skill_match_percentage=metrics["skill_coverage_percentage"],
        baseline_text_score=baseline_similarity,
        semantic_score=semantic_similarity,
        preferred_skill_bonus=preferred_bonus
    )

    overall_score = score_data["overall_score"]
    recommendation = score_data["recommendation"]
    score_breakdown = score_data["score_breakdown"]

    # Format unified matched_skills list combining exact/alias and related for UI presentation
    unified_matched_list = []
    for m in matched_required:
        unified_matched_list.append({
            "skill": m["skill"],
            "match_type": m["match_type"],
            "surface_form_detected": m["surface_form_detected"],
            "evidence": m["evidence"],
            "evidence_category": m["evidence_category"],
            "transferable_credit": m["transferable_credit"],
            "is_required": True,
            "is_related": False,
        })

    for r in related_matches:
        unified_matched_list.append({
            "skill": r["required_skill"],
            "match_type": "Related skill",
            "candidate_related_skill": r["candidate_related_skill"],
            "relationship": r["relationship"],
            "surface_form_detected": r["candidate_related_skill"],
            "evidence": r["evidence"],
            "evidence_category": r["evidence_category"],
            "transferable_credit": r["transferable_credit"],
            "is_required": True,
            "is_related": True,
        })

    # 9. Structure Result
    result = {
        "status": "success",
        "request_id": request_id,
        "resume_filename": resume_meta["filename"],
        "jd_filename": jd_meta["filename"],
        "analysis_method": active_method,
        "overall_score": overall_score,
        "recommendation": recommendation,
        "required_skills_total": metrics["required_skills_total"],
        "required_skills_matched": metrics["exact_alias_matched_count"],
        "skill_match_percentage": metrics["skill_coverage_percentage"],
        "matched_skills": unified_matched_list,
        "related_matches": related_matches,
        "missing_required_skills": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "additional_skills": additional_skills,
        "semantic_similarity": semantic_similarity,
        "lexical_similarity": round(baseline_similarity, 4),
        "score_breakdown": score_breakdown,
        "coverage_metrics": metrics,
        "section_certainty": section_certainty,
        "detected_sections": detected_sections,
        "experience_findings": resume_entities.get("experience", []),
        "education_findings": resume_entities.get("education", []),
        "certifications_findings": resume_entities.get("certifications", []),
        "roles_findings": resume_entities.get("roles", []),
        "warnings": warnings,
        "processing_metadata": {
            "resume_meta": resume_meta,
            "jd_meta": jd_meta,
            "pipeline_version": "1.1.0",
        }
    }

    return result
