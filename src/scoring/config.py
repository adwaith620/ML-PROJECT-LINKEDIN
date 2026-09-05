"""
Configuration for Candidate Scoring and Recommendations.
Contains customizable weights and thresholds for explainable scoring.
"""

# -------------------------------------------------------------------------
# Scoring Weights
# -------------------------------------------------------------------------
# These dictate how much each sub-score contributes to the final 0-100 score.
# They should sum to 1.0.

# If Phase 5 Semantic Matching is NOT active:
DEFAULT_WEIGHTS_NO_SEMANTIC = {
    "skill_match": 0.60,      # 60% weight on structured skills matching
    "text_baseline": 0.40,    # 40% weight on Phase 4 TF-IDF cosine similarity
    "semantic_match": 0.0     # 0% (Inactive)
}

# If Phase 5 Semantic Matching IS active:
DEFAULT_WEIGHTS_WITH_SEMANTIC = {
    "skill_match": 0.40,      # 40% weight on structured skills
    "text_baseline": 0.20,    # 20% weight on TF-IDF
    "semantic_match": 0.40    # 40% weight on Phase 5 Sentence-BERT
}

# -------------------------------------------------------------------------
# Recommendation Thresholds
# -------------------------------------------------------------------------
# Used to map a continuous score [0, 100] into an interpretable category.

RECOMMENDATION_THRESHOLDS = {
    "Strong Match": 80.0,
    "Moderate Match": 60.0,
    "Potential Match": 40.0,
    # Anything below 40 is "Low Match"
}

# -------------------------------------------------------------------------
# Skill Normalization Map
# -------------------------------------------------------------------------
# A baseline dictionary to normalize common technology aliases.
# Can be expanded with a full taxonomy later.

SKILL_NORMALIZATION_MAP = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "js": "javascript",
    "node": "node.js",
    "react": "react.js",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "k8s": "kubernetes",
    "golang": "go",
    "vue": "vue.js",
    "c++": "c++",
    "c#": "c#"
}
