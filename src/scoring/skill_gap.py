"""
skill_gap.py

Module for Skill Gap Analysis.
Handles skill normalization, and calculates matched, missing, and extra skills.
Uses centralized taxonomy aliases.
"""
from typing import List, Dict, Set, Any
from src.skill_extraction.skill_dictionary import ALIAS_MAP

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string to lower-case, stripped, and mapped 
    through the centralized alias dictionary.
    """
    if not skill or not isinstance(skill, str):
        return ""
        
    s_clean = skill.strip().lower()
    if s_clean in ALIAS_MAP:
        return ALIAS_MAP[s_clean].lower()
    return s_clean

def analyze_skill_gap(candidate_skills: List[str], required_skills: List[str], optional_skills: List[str] = None) -> Dict[str, Any]:
    """
    Compare candidate skills against job requirements.
    
    Returns a dictionary containing:
    - matched_required: Skills the candidate has that are required.
    - matched_optional: Skills the candidate has that are optional.
    - missing_required: Required skills the candidate lacks.
    - missing_optional: Optional skills the candidate lacks.
    - additional_skills: Skills the candidate has that were not required or optional.
    - match_percentage: (matched_required / total_required) * 100
    """
    optional_skills = optional_skills or []
    
    # Normalize input lists
    cand_set = {normalize_skill(s) for s in candidate_skills if normalize_skill(s)}
    req_set = {normalize_skill(s) for s in required_skills if normalize_skill(s)}
    opt_set = {normalize_skill(s) for s in optional_skills if normalize_skill(s)}
    
    # Calculate intersections and differences
    matched_required = cand_set.intersection(req_set)
    matched_optional = cand_set.intersection(opt_set)
    
    missing_required = req_set.difference(cand_set)
    missing_optional = opt_set.difference(cand_set)
    
    additional = cand_set.difference(req_set).difference(opt_set)
    
    # Calculate match percentage
    if not req_set:
        match_percentage = 100.0 if cand_set else 0.0
    else:
        match_percentage = (len(matched_required) / len(req_set)) * 100.0
        
    return {
        "matched_required": sorted(list(matched_required)),
        "matched_optional": sorted(list(matched_optional)),
        "missing_required": sorted(list(missing_required)),
        "missing_optional": sorted(list(missing_optional)),
        "additional_skills": sorted(list(additional)),
        "match_percentage": round(match_percentage, 2)
    }
