"""
pipeline.py

Unified Resume Screening & Skill Gap Analysis Pipeline.
Orchestrates:
1. File validation & text extraction (PDF, DOCX, TXT)
2. Text cleaning & normalization (preserving technical tokens)
3. Skill and entity extraction
4. Sentence-level non-fabricated evidence extraction
5. Classical & semantic similarity matching
6. Skill gap analysis & candidate scoring
7. Structured report generation with warnings and processing metadata
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
from src.skill_extraction.extractor import extract_from_resume, extract_from_job
from src.scoring.skill_gap import analyze_skill_gap
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


def extract_evidence_snippets(text: str, skills: List[str], max_snippets: int = 1) -> Dict[str, List[str]]:
    """
    Extracts genuine, non-fabricated sentence snippets from text where skills appear.
    Searches for both canonical names and known surface aliases (e.g. 'AWS' for 'amazon web services').
    """
    if not text or not skills:
        return {}

    from src.skill_extraction.skill_dictionary import ALIAS_MAP
    from src.scoring.skill_gap import normalize_skill

    # Invert ALIAS_MAP to find surface forms for each canonical name
    canonical_to_aliases: Dict[str, List[str]] = {}
    for alias, canonical in ALIAS_MAP.items():
        norm_canonical = normalize_skill(canonical)
        canonical_to_aliases.setdefault(norm_canonical, []).append(alias)
        canonical_to_aliases.setdefault(norm_canonical, []).append(canonical)
        canonical_to_aliases.setdefault(alias.lower(), []).append(canonical)

    # Split text into rough sentences
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    evidence: Dict[str, List[str]] = {}

    for skill in skills:
        skill_lower = skill.lower()
        search_terms = {skill_lower}
        if skill_lower in canonical_to_aliases:
            search_terms.update(canonical_to_aliases[skill_lower])

        # Build regex for these search terms
        sorted_terms = sorted(search_terms, key=len, reverse=True)
        escaped_terms = [re.escape(t) for t in sorted_terms]
        pattern = re.compile(r'(?<![\w])(?:' + '|'.join(escaped_terms) + r')(?![\w])', re.IGNORECASE)

        found = []
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) >= 5 and pattern.search(s_clean):
                clean_s = re.sub(r'\s+', ' ', s_clean)
                if len(clean_s) > 160:
                    clean_s = clean_s[:157] + "..."
                found.append(clean_s)
                if len(found) >= max_snippets:
                    break
        evidence[skill] = found

    return evidence


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

    # 4. Extract Skills and Entities
    resume_entities = extract_from_resume(cleaned_resume)
    jd_entities = extract_from_job(cleaned_jd)

    cand_skills_canonical = [item["canonical"] for item in resume_entities.get("skills", [])]
    req_skills_canonical = [item["canonical"] for item in jd_entities.get("skills", [])]

    if not req_skills_canonical:
        warnings.append(
            "No explicit technical skills from the standard taxonomy were detected in the job description. "
            "Skill coverage score is calculated based on available content."
        )

    if not cand_skills_canonical:
        warnings.append(
            "No technical skills from the standard taxonomy were detected in the resume."
        )

    # 5. Skill Gap Analysis
    gap_analysis = analyze_skill_gap(
        candidate_skills=cand_skills_canonical,
        required_skills=req_skills_canonical
    )

    matched_skills = gap_analysis["matched_required"]
    missing_required = gap_analysis["missing_required"]
    additional_skills = gap_analysis["additional_skills"]
    skill_match_pct = gap_analysis["match_percentage"]

    # 6. Evidence Snippet Extraction (Genuine, from resume)
    evidence_map = extract_evidence_snippets(cleaned_resume, matched_skills)

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
            # Ensure model loaded
            if matcher.load_model():
                raw_sem = matcher.compute_similarity(cleaned_resume, cleaned_jd)
                # Cosine similarity in [-1, 1], clamp to [0, 1] for positive similarity
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
    score_data = calculate_candidate_score(
        skill_match_percentage=skill_match_pct,
        baseline_text_score=baseline_similarity,
        semantic_score=semantic_similarity
    )

    overall_score = score_data["overall_score"]
    recommendation = score_data["recommendation"]
    score_breakdown = score_data["score_breakdown"]

    # 9. Structure Result
    result = {
        "status": "success",
        "request_id": request_id,
        "resume_filename": resume_meta["filename"],
        "jd_filename": jd_meta["filename"],
        "analysis_method": active_method,
        "overall_score": overall_score,
        "recommendation": recommendation,
        "required_skills_total": len(req_skills_canonical),
        "required_skills_matched": len(matched_skills),
        "skill_match_percentage": skill_match_pct,
        "matched_skills": [
            {
                "skill": s,
                "evidence": evidence_map.get(s, [])
            } for s in matched_skills
        ],
        "missing_required_skills": missing_required,
        "additional_skills": additional_skills,
        "semantic_similarity": semantic_similarity,
        "lexical_similarity": round(baseline_similarity, 4),
        "score_breakdown": score_breakdown,
        "experience_findings": resume_entities.get("experience", []),
        "education_findings": resume_entities.get("education", []),
        "certifications_findings": resume_entities.get("certifications", []),
        "roles_findings": resume_entities.get("roles", []),
        "warnings": warnings,
        "processing_metadata": {
            "resume_meta": resume_meta,
            "jd_meta": jd_meta,
            "pipeline_version": "1.0.0",
        }
    }

    return result
