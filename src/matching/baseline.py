"""
Baseline matching algorithms for Resume-Job Fit.
Uses classical machine learning models and TF-IDF representations.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import paired_cosine_distances
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

class BaselineFeatureExtractor:
    """Extracts classical ML features from resume and JD pairs."""
    
    def __init__(self, max_features: int = 5000):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
        self.is_fitted = False
        
    def fit(self, texts: List[str]):
        """Fit the TF-IDF vectorizer on a corpus of text (e.g. combined training resumes and JDs)."""
        # Filter out empty strings and nulls to avoid warnings
        valid_texts = [t if isinstance(t, str) and t.strip() else "empty" for t in texts]
        self.vectorizer.fit(valid_texts)
        self.is_fitted = True
        return self
        
    def transform(self, resumes: List[str], jds: List[str]) -> pd.DataFrame:
        """
        Generate feature dataframe containing:
        - TF-IDF cosine similarity
        - Resume length & word count
        - JD length & word count
        """
        if not self.is_fitted:
            raise ValueError("Extractor must be fitted before transform.")
            
        resumes = [t if isinstance(t, str) and t.strip() else "" for t in resumes]
        jds = [t if isinstance(t, str) and t.strip() else "" for t in jds]
        
        # Transform text
        X_res = self.vectorizer.transform(resumes)
        X_jd = self.vectorizer.transform(jds)
        
        # Compute cosine similarity (1 - cosine distance)
        # paired_cosine_distances returns distance, so similarity is 1 - distance
        cosine_sim = 1.0 - paired_cosine_distances(X_res, X_jd)
        
        # Build features dataframe
        features = pd.DataFrame({
            'tfidf_cosine_similarity': cosine_sim,
            'resume_char_len': [len(t) for t in resumes],
            'resume_word_count': [len(t.split()) for t in resumes],
            'jd_char_len': [len(t) for t in jds],
            'jd_word_count': [len(t.split()) for t in jds],
        })
        
        # Additional relative features
        features['length_ratio'] = features['resume_char_len'] / (features['jd_char_len'] + 1e-5)
        
        return features

def train_baseline_model(X_train: pd.DataFrame, y_train: pd.Series, model_type: str = 'logistic_regression', class_weight: str = 'balanced') -> Any:
    """
    Train a baseline classifier.
    Supported model_types: 'logistic_regression', 'linear_svm', 'random_forest'
    """
    if model_type == 'logistic_regression':
        model = LogisticRegression(class_weight=class_weight, random_state=42, max_iter=1000)
    elif model_type == 'linear_svm':
        model = LinearSVC(class_weight=class_weight, random_state=42, max_iter=2000)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(class_weight=class_weight, random_state=42, n_estimators=100)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
        
    model.fit(X_train, y_train)
    return model

def evaluate_model(model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """Evaluate a trained model, returning metrics and confusion matrix."""
    predictions = model.predict(X_test)
    
    # Class probabilities if supported
    probs = None
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_test)
        
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, predictions)
    
    return {
        'predictions': predictions,
        'probabilities': probs,
        'classification_report': report,
        'confusion_matrix': cm
    }
