"""
candidate_score.py

Module for Candidate Scoring.
Aggregates skill matches and ML baseline/semantic text scores into a final weighted score.
Supports transparent breakdowns, fallback modes, and documented preferred skill bonus.
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
    semantic_score: Optional[float] = None,
    preferred_skill_bonus: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate an overall weighted score.
    
    If semantic_score is None (offline or Sentence-BERT unavailable), the weights 
    adjust automatically to the classical fallback configuration (60% skills, 40% TF-IDF).
    Both text scores are expected to be in the [0, 1] range and will be scaled to [0, 100].
    
    Preferred skills bonus is added directly to the total (capped at 5.0 pts).
    The final score is strictly bounded in [0.0, 100.0].
    
    Returns a dictionary with the final score, the breakdown, and the recommendation.
    """
    # Select weights based on semantic availability
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
    
    # Cap preferred skill bonus at 5.0 points
    bounded_pref_bonus = max(0.0, min(5.0, preferred_skill_bonus))
    
    final_score = score_skills + score_baseline + score_semantic + bounded_pref_bonus
    
    # Bound the total score
    final_score = max(0.0, min(100.0, final_score))
    
    return {
        "overall_score": round(final_score, 2),
        "recommendation": determine_recommendation(final_score),
        "score_breakdown": {
            "skill_contribution": round(score_skills, 2),
            "baseline_text_contribution": round(score_baseline, 2),
            "semantic_text_contribution": round(score_semantic, 2),
            "preferred_skill_bonus": round(bounded_pref_bonus, 2),
            "weights_used": weights
        }
    }
