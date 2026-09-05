"""
Evaluation and Explainability module for the Resume Screening System.
Provides tools for comparing models, analyzing errors, checking data leakage,
and generating interpretable candidate scoring explanations.
"""

from .metrics import calculate_classification_metrics, get_confusion_matrix
from .model_comparison import compare_models
from .error_analysis import identify_errors
from .explainability import generate_candidate_explanation
from .leakage import check_data_leakage
