"""
match_classifier.py

Classifies skill matches between resumes and job descriptions into precise categories:
1. Exact match: Candidate explicitly wrote the requested canonical skill.
2. Recognized alias: Candidate used an accepted synonym/alias (e.g. AWS vs Amazon Web Services).
3. Related or transferable skill: Candidate demonstrates a related competency (e.g. PostgreSQL for MySQL).
4. Not evidenced: No evidence of the skill or related competency in the resume.

Also extracts high-quality, non-redundant, prioritized sentence evidence snippets
categorized by section (Work Experience, Project Evidence, Education, Skills List).
"""

import re
from typing import Dict, List, Set, Any, Optional, Tuple
from .skill_dictionary import ALIAS_MAP, RELATED_SKILLS_MAP, get_all_skills


# Sections typically found in resumes
RESUME_SECTION_PATTERNS = {
    "work_experience": re.compile(
        r'^(?:[#*=-]+\s*)?(?:professional\s+|work\s+)?(?:experience|employment|work\s+history|career\s+history)[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
    "projects": re.compile(
        r'^(?:[#*=-]+\s*)?(?:key\s+|technical\s+|academic\s+|personal\s+)?projects?[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
    "education_certification": re.compile(
        r'^(?:[#*=-]+\s*)?(?:education|certifications?|credentials?|academic\s+background)[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
    "skills_list": re.compile(
        r'^(?:[#*=-]+\s*)?(?:technical\s+|core\s+|key\s+)?(?:skills|competencies|technologies|tools|stack)[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
}


def segment_resume_sentences(resume_text: str) -> List[Dict[str, str]]:
    """
    Splits resume text into individual sentences/bullet points with section tagging.
    Returns list of dicts: {"text": str, "section": str}.
    """
    lines = resume_text.splitlines()
    segmented: List[Dict[str, str]] = []
    current_section = "general"

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Check if line is a section header
        new_section = None
        for sec_name, pattern in RESUME_SECTION_PATTERNS.items():
            if pattern.match(line_clean):
                new_section = sec_name
                break

        if new_section:
            current_section = new_section
            continue

        # Break line or bullet into sentences
        bullet_clean = re.sub(r'^[•\-\*\u2022\u2023]\s*', '', line_clean)
        sentences = re.split(r'(?<=[.!?])\s+', bullet_clean)
        for s in sentences:
            s_str = s.strip()
            if len(s_str) >= 5:
                segmented.append({
                    "text": s_str,
                    "section": current_section
                })

    return segmented


def get_search_terms_for_skill(canonical_skill: str) -> List[str]:
    """
    Returns all search terms (canonical name and recognized aliases) for a skill,
    ordered by length descending.
    """
    terms = {canonical_skill.lower()}
    for alias, canon in ALIAS_MAP.items():
        if canon.lower() == canonical_skill.lower():
            terms.add(alias.lower())

    sorted_terms = sorted(list(terms), key=len, reverse=True)
    return sorted_terms


def extract_best_evidence_for_skill(
    canonical_skill: str,
    segmented_sentences: List[Dict[str, str]],
    used_snippets: Set[str]
) -> Tuple[Optional[str], str]:
    """
    Finds the most specific, non-redundant evidence snippet for a skill.
    Prioritizes:
    1. Work Experience
    2. Projects
    3. Education / Certification
    4. Skills List (only if not found in experience/projects)
    
    Avoids reusing the exact same long list snippet across multiple skills when
    a more specific project/work sentence exists.
    """
    search_terms = get_search_terms_for_skill(canonical_skill)
    escaped = [re.escape(t) for t in search_terms]
    pattern = re.compile(r'(?<![\w])(?:' + '|'.join(escaped) + r')(?![\w])', re.IGNORECASE)

    candidates_by_priority = {
        "work_experience": [],
        "projects": [],
        "education_certification": [],
        "skills_list": [],
        "general": []
    }

    for item in segmented_sentences:
        text = item["text"]
        sec = item["section"]
        if pattern.search(text):
            candidates_by_priority.setdefault(sec, []).append(text)

    # Priority order
    section_order = [
        ("work_experience", "Work Experience"),
        ("projects", "Project Evidence"),
        ("education_certification", "Education & Certification"),
        ("skills_list", "Skills Section"),
        ("general", "Resume Text")
    ]

    for sec_key, human_label in section_order:
        snippets = candidates_by_priority.get(sec_key, [])
        # Find first unused snippet, or fallback to first snippet if all used
        unused = [s for s in snippets if s not in used_snippets]
        best_snippet = unused[0] if unused else (snippets[0] if snippets else None)

        if best_snippet:
            # Clean snippet for display
            clean_snippet = re.sub(r'\s+', ' ', best_snippet)
            if len(clean_snippet) > 180:
                clean_snippet = clean_snippet[:177] + "..."
            used_snippets.add(best_snippet)
            return clean_snippet, human_label

    return None, "Evidence not available"


def classify_skill_matches(
    resume_skills_dict: List[Dict[str, Any]],
    required_skills: List[str],
    preferred_skills: List[str],
    resume_text: str
) -> Dict[str, Any]:
    """
    Evaluates candidate skills against required and preferred skills.
    
    Categorizes each required skill into:
    - EXACT: Explicit canonical skill demonstrated.
    - ALIAS: Recognized alternative name used (e.g. AWS for Amazon Web Services).
    - RELATED: Transferable skill demonstrated (e.g. PostgreSQL for MySQL).
    - NOT_EVIDENCED: Not found in resume.
    """
    segmented_sentences = segment_resume_sentences(resume_text)
    used_snippets: Set[str] = set()

    # Map candidate canonical skills to surface forms used
    cand_canonical_to_surface: Dict[str, List[str]] = {}
    for item in resume_skills_dict:
        if isinstance(item, str):
            canon = item.strip()
            surfaces = [canon]
        elif isinstance(item, dict):
            canon = item.get("canonical") or item.get("skill") or ""
            surfaces = item.get("surface_forms") or ([item["surface_form"]] if "surface_form" in item else [canon])
        else:
            continue
        if canon:
            cand_canonical_to_surface[canon.lower()] = surfaces

    cand_canonical_keys = set(cand_canonical_to_surface.keys())

    matched_required_details: List[Dict[str, Any]] = []
    related_skills_details: List[Dict[str, Any]] = []
    missing_required: List[str] = []

    exact_alias_count = 0
    related_credit_sum = 0.0

    # 1. Process Required Skills
    for req_skill in required_skills:
        req_lower = req_skill.lower()

        if req_lower in cand_canonical_keys:
            # Check whether exact canonical form or alias was used
            surfaces = cand_canonical_to_surface[req_lower]
            is_exact = any(s.strip().lower() == req_skill.lower() for s in surfaces)
            match_type = "Exact match" if is_exact else "Recognized alias"
            alias_used = surfaces[0] if not is_exact else req_skill

            evidence, evidence_cat = extract_best_evidence_for_skill(
                req_skill, segmented_sentences, used_snippets
            )

            matched_required_details.append({
                "skill": req_skill,
                "match_type": match_type,
                "surface_form_detected": alias_used,
                "evidence": [evidence] if evidence else [],
                "evidence_category": evidence_cat,
                "transferable_credit": 1.0,
                "is_required": True,
            })
            exact_alias_count += 1

        else:
            # Check for Related / Transferable skills
            related_candidates = RELATED_SKILLS_MAP.get(req_skill, [])
            found_related = None

            for related_skill_name, relation_desc, credit in related_candidates:
                if related_skill_name.lower() in cand_canonical_keys:
                    found_related = (related_skill_name, relation_desc, credit)
                    break

            if found_related:
                rel_name, rel_desc, rel_credit = found_related
                evidence, evidence_cat = extract_best_evidence_for_skill(
                    rel_name, segmented_sentences, used_snippets
                )

                rel_obj = {
                    "required_skill": req_skill,
                    "candidate_related_skill": rel_name,
                    "relationship": rel_desc,
                    "match_type": "Related skill",
                    "surface_form_detected": rel_name,
                    "evidence": [evidence] if evidence else [],
                    "evidence_category": evidence_cat,
                    "transferable_credit": rel_credit,
                    "is_required": True,
                }
                related_skills_details.append(rel_obj)
                related_credit_sum += rel_credit
            else:
                missing_required.append(req_skill)

    # 2. Process Preferred Skills
    matched_preferred_details: List[Dict[str, Any]] = []
    missing_preferred: List[str] = []

    for pref_skill in preferred_skills:
        pref_lower = pref_skill.lower()
        if pref_lower in cand_canonical_keys:
            surfaces = cand_canonical_to_surface[pref_lower]
            is_exact = any(s.strip().lower() == pref_skill.lower() for s in surfaces)
            match_type = "Exact match" if is_exact else "Recognized alias"

            evidence, evidence_cat = extract_best_evidence_for_skill(
                pref_skill, segmented_sentences, used_snippets
            )

            matched_preferred_details.append({
                "skill": pref_skill,
                "match_type": match_type,
                "surface_form_detected": surfaces[0],
                "evidence": [evidence] if evidence else [],
                "evidence_category": evidence_cat,
                "transferable_credit": 1.0,
                "is_required": False,
            })
        else:
            missing_preferred.append(pref_skill)

    # 3. Additional Skills (skills in resume that were neither required nor preferred)
    all_jd_skills = {s.lower() for s in (required_skills + preferred_skills)}
    additional_skills: List[str] = []
    for cand_lower, surfaces in cand_canonical_to_surface.items():
        if cand_lower not in all_jd_skills:
            # Find proper canonical casing from ALIAS_MAP or fallback
            canonical_name = ALIAS_MAP.get(cand_lower, surfaces[0].title())
            if canonical_name not in additional_skills:
                additional_skills.append(canonical_name)

    additional_skills.sort()

    # 4. Coverage Calculation
    # Required skills denominator is explicitly len(required_skills)
    total_req = len(required_skills)
    if total_req > 0:
        raw_skill_score = ((exact_alias_count * 1.0 + related_credit_sum) / total_req) * 100.0
        skill_coverage_pct = round(min(100.0, max(0.0, raw_skill_score)), 2)
    else:
        # If JD specified no required skills, base coverage on whether any skills exist
        skill_coverage_pct = 100.0 if cand_canonical_keys else 0.0

    return {
        "matched_required": matched_required_details,
        "related_matches": related_skills_details,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred_details,
        "missing_preferred": missing_preferred,
        "additional_skills": additional_skills,
        "metrics": {
            "required_skills_total": total_req,
            "exact_alias_matched_count": exact_alias_count,
            "related_matched_count": len(related_skills_details),
            "missing_required_count": len(missing_required),
            "preferred_skills_total": len(preferred_skills),
            "preferred_skills_matched_count": len(matched_preferred_details),
            "skill_coverage_percentage": skill_coverage_pct,
            "related_credit_awarded": round(related_credit_sum, 2),
            "effective_matched_units": round(exact_alias_count * 1.0 + related_credit_sum, 2),
        }
    }
