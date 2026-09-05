"""
Module for Candidate Ranking.
Processes a list of candidates against a job description, yielding a ranked and explainable list.
"""
from typing import List, Dict, Any, Optional
from .skill_gap import analyze_skill_gap
from .candidate_score import calculate_candidate_score

def rank_candidates(candidates: List[Dict[str, Any]], job_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluate and rank multiple candidates for a single job position.
    
    Expected format for `job_requirements`:
    {
        "required_skills": ["Python", "SQL", ...],
        "optional_skills": ["AWS", ...] (optional)
    }
    
    Expected format for each candidate in `candidates`:
    {
        "candidate_id": "123",
        "candidate_skills": ["Python", "Git", ...],
        "baseline_match_score": 0.85, (optional, float [0, 1])
        "semantic_similarity_score": 0.90 (optional, float [0, 1])
    }
    
    Returns a list of structured explainability outputs, sorted by overall_score descending.
    """
    req_skills = job_requirements.get("required_skills", [])
    opt_skills = job_requirements.get("optional_skills", [])
    
    results = []
    
    for cand in candidates:
        cand_id = cand.get("candidate_id", "Unknown")
        cand_skills = cand.get("candidate_skills", [])
        
        # 1. Skill Gap Analysis
        gap_analysis = analyze_skill_gap(cand_skills, req_skills, opt_skills)
        
        # 2. Scoring
        baseline_score = cand.get("baseline_match_score", 0.0)
        semantic_score = cand.get("semantic_similarity_score", None)
        
        score_details = calculate_candidate_score(
            skill_match_percentage=gap_analysis["match_percentage"],
            baseline_text_score=baseline_score,
            semantic_score=semantic_score
        )
        
        # 3. Compile Explainability Output
        explainable_output = {
            "candidate_id": cand_id,
            "overall_score": score_details["overall_score"],
            "recommendation": score_details["recommendation"],
            "skill_match_percentage": gap_analysis["match_percentage"],
            "matched_skills": gap_analysis["matched_required"],
            "missing_required_skills": gap_analysis["missing_required"],
            "additional_skills": gap_analysis["additional_skills"],
            "score_breakdown": score_details["score_breakdown"]
        }
        
        results.append(explainable_output)
        
    # Sort by overall score descending
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results
