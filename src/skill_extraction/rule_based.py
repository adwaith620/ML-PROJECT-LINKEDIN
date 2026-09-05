"""
rule_based.py

Implements regex and dictionary-based extraction rules for:
- Technical Skills
- Experience (years)
- Degrees/Education
- Certifications
- Job Roles
"""

import re
from .skill_dictionary import (
    get_all_skills, ALIAS_MAP, CERTIFICATIONS, JOB_ROLES, EDUCATION_DEGREES
)

def build_word_boundary_regex(phrases):
    """
    Builds a regex pattern that matches any of the phrases exactly, 
    respecting word boundaries. Escapes regex characters.
    """
    # Sort by length descending to match longest phrases first (e.g. "React.js" before "React")
    sorted_phrases = sorted(phrases, key=len, reverse=True)
    escaped_phrases = [re.escape(p) for p in sorted_phrases]
    
    # We use \b boundary, but watch out for terms starting/ending with non-word chars (like C++)
    # A more robust boundary check for technical terms:
    pattern_str = r'(?<![\w])(?:' + '|'.join(escaped_phrases) + r')(?![\w])'
    return re.compile(pattern_str, re.IGNORECASE)

# Compile regex patterns once
ALL_SKILL_PHRASES = list(set(get_all_skills() + list(ALIAS_MAP.keys())))
SKILLS_REGEX = build_word_boundary_regex(ALL_SKILL_PHRASES)

CERTIFICATIONS_REGEX = build_word_boundary_regex(CERTIFICATIONS)
ROLES_REGEX = build_word_boundary_regex(JOB_ROLES)
EDUCATION_REGEX = build_word_boundary_regex(EDUCATION_DEGREES)

# Experience regex: matches "5 years of experience", "10+ yrs experience", etc.
EXPERIENCE_PATTERN = re.compile(
    r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience',
    re.IGNORECASE
)

def extract_skills_rule_based(text: str) -> list:
    """Extracts raw skill phrases found in the text."""
    if not text:
        return []
    matches = SKILLS_REGEX.findall(text)
    # Deduplicate while preserving case of the first match
    unique_matches = list({m.lower(): m for m in matches}.values())
    return unique_matches

def extract_certifications_rule_based(text: str) -> list:
    if not text:
        return []
    matches = CERTIFICATIONS_REGEX.findall(text)
    return list({m.lower(): m for m in matches}.values())

def extract_roles_rule_based(text: str) -> list:
    if not text:
        return []
    matches = ROLES_REGEX.findall(text)
    return list({m.lower(): m for m in matches}.values())

def extract_education_rule_based(text: str) -> list:
    if not text:
        return []
    matches = EDUCATION_REGEX.findall(text)
    return list({m.lower(): m for m in matches}.values())

def extract_experience_rule_based(text: str) -> list:
    """Extracts stated years of experience."""
    if not text:
        return []
    matches = EXPERIENCE_PATTERN.findall(text)
    
    # Optional: convert matches to standard format like "5 years"
    res = []
    for m in matches:
        res.append(f"{m} years")
        
    return list(set(res))
