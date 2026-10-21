"""
config.py

Configuration for Candidate Scoring and Recommendations.
Contains customizable weights, recommendation thresholds, and links to the centralized taxonomy.
"""
from src.skill_extraction.skill_dictionary import ALIAS_MAP, RELATED_SKILLS_MAP

# -------------------------------------------------------------------------
# Scoring Weights
# -------------------------------------------------------------------------
# Default weights when Sentence-BERT is offline:
DEFAULT_WEIGHTS_NO_SEMANTIC = {
    "skill_match": 0.60,      # 60% weight on structured skills matching
    "text_baseline": 0.40,    # 40% weight on TF-IDF cosine similarity
    "semantic_match": 0.0     # 0% (Inactive)
}

# Default weights when Sentence-BERT is active:
DEFAULT_WEIGHTS_WITH_SEMANTIC = {
    "skill_match": 0.40,      # 40% weight on structured skills
    "text_baseline": 0.20,    # 20% weight on TF-IDF
    "semantic_match": 0.40    # 40% weight on Sentence-BERT
}

# -------------------------------------------------------------------------
# Recommendation Thresholds
# -------------------------------------------------------------------------
RECOMMENDATION_THRESHOLDS = {
    "Strong Match": 80.0,
    "Moderate Match": 60.0,
    "Potential Match": 40.0,
    # Anything below 40 is "Low Match"
}

# Legacy lowercase normalization map (for backward compatibility)
SKILL_NORMALIZATION_MAP = {k: v.lower() for k, v in ALIAS_MAP.items()}
