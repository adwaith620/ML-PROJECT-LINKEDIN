"""
extractor.py

Main interface for Phase 3 skill and entity extraction.
Provides generic APIs for extracting data from both resumes and job descriptions.

Input: Cleaned text string (from Phase 2)
Output: Structured JSON-compatible dictionary
"""

import uuid
from .rule_based import (
    extract_skills_rule_based,
    extract_roles_rule_based,
    extract_education_rule_based,
    extract_certifications_rule_based,
    extract_experience_rule_based
)
from .normalization import normalize_skill_list

def extract_from_resume(cleaned_resume_text: str, record_id: str = None) -> dict:
    """
    Extracts entities from a cleaned resume string.
    Returns a structured dictionary.
    """
    if record_id is None:
        record_id = str(uuid.uuid4())
        
    raw_skills = extract_skills_rule_based(cleaned_resume_text)
    normalized_skills = normalize_skill_list(raw_skills)
    
    roles = extract_roles_rule_based(cleaned_resume_text)
    education = extract_education_rule_based(cleaned_resume_text)
    certifications = extract_certifications_rule_based(cleaned_resume_text)
    experience = extract_experience_rule_based(cleaned_resume_text)
    
    return {
        "record_id": record_id,
        "skills": normalized_skills,
        "roles": roles,
        "education": education,
        "certifications": certifications,
        "experience": experience
    }

def extract_from_job(cleaned_job_text: str, job_id: str = None) -> dict:
    """
    Extracts entities from a cleaned job description string.
    Returns a structured dictionary.
    """
    if job_id is None:
        job_id = str(uuid.uuid4())
        
    raw_skills = extract_skills_rule_based(cleaned_job_text)
    normalized_skills = normalize_skill_list(raw_skills)
    
    roles = extract_roles_rule_based(cleaned_job_text)
    education = extract_education_rule_based(cleaned_job_text)
    experience = extract_experience_rule_based(cleaned_job_text)
    
    return {
        "job_id": job_id,
        "skills": normalized_skills,
        "roles": roles,
        "education_requirements": education,
        "experience_requirements": experience
    }
