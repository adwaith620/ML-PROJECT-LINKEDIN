"""
jd_parser.py

Intelligent Job Description parser that segments JDs into:
- Required Qualifications / Must-Haves
- Preferred Qualifications / Nice-to-Haves
- Responsibilities / Context / Overview

Extracts and categorizes skills as required, preferred, or contextual.
Preserves uncertainty when section classification is ambiguous.
"""

import re
from typing import Dict, List, Set, Any, Tuple
from .rule_based import extract_skills_rule_based
from .normalization import normalize_skill_list


# Regex patterns for identifying JD section headings
SECTION_PATTERNS = {
    "required": re.compile(
        r'^(?:[#*=-]+\s*)?(?:(?:minimum|basic|required|core|mandatory|key|technical|job)\s+)?'
        r'(?:requirements|qualifications|skills|must\s*haves?|what\s*(?:you|you\'ll)\s*need|who\s*you\s*are)'
        r'[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
    "preferred": re.compile(
        r'^(?:[#*=-]+\s*)?'
        r'(?:(?:preferred|desired|bonus|additional|secondary)\s*(?:qualifications|skills|requirements)?|nice\s*to\s*haves?|good\s*to\s*haves?|plus(?:es)?|what\s*gives\s*you\s*an\s*edge)'
        r'[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
    "responsibilities": re.compile(
        r'^(?:[#*=-]+\s*)?(?:key\s+)?(?:responsibilities|duties|what\s*(?:you\'ll|you\s*will)\s*do|role\s*(?:overview|description)|day\s*to\s*day)'
        r'[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
    "context": re.compile(
        r'^(?:[#*=-]+\s*)?(?:about\s*(?:us|the\s*company|the\s*team|the\s*role)|company\s*overview|who\s*we\s*are|our\s*mission)'
        r'[:\s-]*$',
        re.IGNORECASE | re.MULTILINE
    ),
}

# Sentence-level cue phrases for when section headers are absent
REQUIRED_CUE_PHRASES = [
    r'\bmust\s+have\b',
    r'\brequired\b',
    r'\bessential\b',
    r'\bmandatory\b',
    r'\bminimum\s+of\b',
    r'\bproficient\s+in\b',
    r'\bproven\s+experience\b',
    r'\bstrong\s+knowledge\s+of\b',
    r'\bstrong\s+proficiency\b',
    r'\bhands-on\s+experience\b',
    r'\bexpert\s+in\b',
    r'\b\d+\+?\s*years?\s+(?:of\s+)?experience\b',
]

PREFERRED_CUE_PHRASES = [
    r'\bnice\s+to\s+have\b',
    r'\bgood\s+to\s+have\b',
    r'\bbonus\b',
    r'\bpreferred\b',
    r'\bdesirable\b',
    r'\ba\s+plus\b',
    r'\bfamiliarity\s+with\b',
    r'\badvantage\b',
    r'\bexposure\s+to\b',
    r'\boptional\b',
    r'\bideal(?:ly)?\b',
]

REQUIRED_CUE_REGEX = re.compile('|'.join(REQUIRED_CUE_PHRASES), re.IGNORECASE)
PREFERRED_CUE_REGEX = re.compile('|'.join(PREFERRED_CUE_PHRASES), re.IGNORECASE)


def split_jd_into_sections(text: str) -> Dict[str, str]:
    """
    Identifies section headers and splits JD into labeled text blocks.
    Returns a dictionary mapping section types to their respective text content.
    """
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {
        "required": [],
        "preferred": [],
        "responsibilities": [],
        "context": [],
        "unclassified": []
    }

    current_section = "unclassified"

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        matched_section = None
        for sec_type, pattern in SECTION_PATTERNS.items():
            if pattern.match(line_stripped):
                matched_section = sec_type
                break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Parses a job description to separate required, preferred, and contextual skills.
    
    Returns:
    {
        "required_skills": List[str],      # Canonical names of required skills
        "preferred_skills": List[str],     # Canonical names of preferred skills
        "contextual_skills": List[str],    # Canonical names of contextual/supporting skills
        "section_certainty": "explicit" | "inferred",
        "detected_sections": List[str],
        "all_skills_detailed": List[Dict]  # Structured skill objects with canonical and aliases
    }
    """
    if not jd_text or not jd_text.strip():
        return {
            "required_skills": [],
            "preferred_skills": [],
            "contextual_skills": [],
            "section_certainty": "inferred",
            "detected_sections": [],
            "all_skills_detailed": []
        }

    sections = split_jd_into_sections(jd_text)
    detected_section_keys = [k for k in sections if k != "unclassified"]

    required_raw: List[str] = []
    preferred_raw: List[str] = []
    contextual_raw: List[str] = []
    section_certainty = "explicit" if ("required" in sections or "preferred" in sections) else "inferred"

    if section_certainty == "explicit":
        # Extract from labeled sections
        if "required" in sections:
            required_raw.extend(extract_skills_rule_based(sections["required"]))
        if "preferred" in sections:
            preferred_raw.extend(extract_skills_rule_based(sections["preferred"]))
        if "responsibilities" in sections:
            contextual_raw.extend(extract_skills_rule_based(sections["responsibilities"]))
        if "context" in sections:
            contextual_raw.extend(extract_skills_rule_based(sections["context"]))
        if "unclassified" in sections:
            # Fallback sentence parsing for remaining unclassified text
            for sentence in re.split(r'(?<=[.!?\n])\s+', sections["unclassified"]):
                if not sentence.strip():
                    continue
                skills = extract_skills_rule_based(sentence)
                if not skills:
                    continue
                if PREFERRED_CUE_REGEX.search(sentence):
                    preferred_raw.extend(skills)
                elif REQUIRED_CUE_REGEX.search(sentence):
                    required_raw.extend(skills)
                else:
                    contextual_raw.extend(skills)
    else:
        # No explicit section headers; use sentence-level heuristic
        for sentence in re.split(r'(?<=[.!?\n])\s+', jd_text):
            if not sentence.strip():
                continue
            skills = extract_skills_rule_based(sentence)
            if not skills:
                continue
            if PREFERRED_CUE_REGEX.search(sentence):
                preferred_raw.extend(skills)
            elif REQUIRED_CUE_REGEX.search(sentence):
                required_raw.extend(skills)
            else:
                # In single-paragraph JDs without explicit headers, technical mentions default to required
                required_raw.extend(skills)

    # Normalize extracted skill sets
    norm_req = normalize_skill_list(required_raw)
    norm_pref = normalize_skill_list(preferred_raw)
    norm_ctx = normalize_skill_list(contextual_raw)

    req_set = {item["canonical"] for item in norm_req}
    # Preferred skills should not duplicate required skills (required takes precedence)
    pref_set = {item["canonical"] for item in norm_pref} - req_set
    # Contextual skills should not duplicate required or preferred
    ctx_set = {item["canonical"] for item in norm_ctx} - req_set - pref_set

    # If sentence-level heuristic found nothing as required but found preferred/contextual,
    # promote contextual to required to avoid empty denominator if skills exist
    if not req_set and ctx_set:
        req_set = ctx_set
        ctx_set = set()

    all_detailed = normalize_skill_list(required_raw + preferred_raw + contextual_raw)

    return {
        "required_skills": sorted(list(req_set)),
        "preferred_skills": sorted(list(pref_set)),
        "contextual_skills": sorted(list(ctx_set)),
        "section_certainty": section_certainty,
        "detected_sections": detected_section_keys,
        "all_skills_detailed": all_detailed
    }
