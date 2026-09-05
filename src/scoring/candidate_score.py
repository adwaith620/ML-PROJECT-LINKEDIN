"""
Module for Candidate Scoring.
Aggregates skill matches and ML baseline/semantic text scores into a final weighted score.
"""
from typing import Dict, Any, Optional
from .config import DEFAULT_WEIGHTS_NO_SEMANTIC, DEFAULT_WEIGHTS_WITH_SEMANTIC, RECOMMENDATION_THRESHOLDS

def determine_recommendation(score: float) -> str:
    """Map a numerical score [0, 100] to a categorical recommendation."""
    if score >= RECOMMENDATION_THRESHOLDS["Strong Match"]:
        return "Strong Match"
    elif score >= RECOMMENDATION_THRESHOLDS["Moderate Match"]:
        return "Moderate Match"
    elif score >= RECOMMENDATION_THRESHOLDS["Potential Match"]:
        return "Potential Match"
    else:
        return "Low Match"

def calculate_candidate_score(
    skill_match_percentage: float, 
    baseline_text_score: float = 0.0, 
    semantic_score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate an overall weighted score.
    
    If semantic_score is None (Phase 5 not integrated), the weights adjust 
    automatically to ignore it. Both text scores are expected to be in the [0, 1] range
    and will be scaled to [0, 100].
    
    Returns a dictionary with the final score, the breakdown, and the recommendation.
    """
    # Select weights based on Phase 5 integration status
    if semantic_score is None:
        weights = DEFAULT_WEIGHTS_NO_SEMANTIC
        semantic_val = 0.0
    else:
        weights = DEFAULT_WEIGHTS_WITH_SEMANTIC
        semantic_val = semantic_score * 100.0  # Scale [0,1] to [0,100]
        
    baseline_val = baseline_text_score * 100.0  # Scale [0,1] to [0,100]
    
    # Calculate weighted components
    score_skills = skill_match_percentage * weights["skill_match"]
    score_baseline = baseline_val * weights["text_baseline"]
    score_semantic = semantic_val * weights["semantic_match"]
    
    final_score = score_skills + score_baseline + score_semantic
    
    # Bound the score
    final_score = max(0.0, min(100.0, final_score))
    
    return {
        "overall_score": round(final_score, 2),
        "recommendation": determine_recommendation(final_score),
        "score_breakdown": {
            "skill_contribution": round(score_skills, 2),
            "baseline_text_contribution": round(score_baseline, 2),
            "semantic_text_contribution": round(score_semantic, 2),
            "weights_used": weights
        }
    }
