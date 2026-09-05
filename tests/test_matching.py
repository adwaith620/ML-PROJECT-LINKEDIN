import pytest
import pandas as pd
import numpy as np
from src.matching.baseline import BaselineFeatureExtractor, train_baseline_model

def test_feature_extractor_fit_transform():
    extractor = BaselineFeatureExtractor(max_features=10)
    
    # Train corpus
    corpus = [
        "python developer with django and flask",
        "java engineer with spring boot",
        "looking for python developer",
        "seeking java engineer"
    ]
    
    extractor.fit(corpus)
    assert extractor.is_fitted
    
    # Test transform
    resumes = ["python django", "java spring"]
    jds = ["need python", "need java"]
    
    features = extractor.transform(resumes, jds)
    
    assert isinstance(features, pd.DataFrame)
    assert len(features) == 2
    assert "tfidf_cosine_similarity" in features.columns
    assert "resume_char_len" in features.columns
    assert "length_ratio" in features.columns
    
    # Check similarity is bounded [0, 1] (or very close due to float precision)
    assert (features["tfidf_cosine_similarity"] >= -0.01).all()
    assert (features["tfidf_cosine_similarity"] <= 1.01).all()

def test_feature_extractor_empty_handling():
    extractor = BaselineFeatureExtractor(max_features=10)
    extractor.fit(["valid text"])
    
    # Empty texts
    resumes = ["", None]
    jds = ["", "some text"]
    
    features = extractor.transform(resumes, jds)
    assert len(features) == 2
    # Should not crash and should produce 0 length
    assert features.loc[0, "resume_char_len"] == 0
    assert features.loc[1, "resume_char_len"] == 0

def test_train_baseline_model():
    X_train = pd.DataFrame({
        "tfidf_cosine_similarity": [0.9, 0.1, 0.8, 0.2],
        "resume_char_len": [100, 100, 100, 100],
        "resume_word_count": [10, 10, 10, 10],
        "jd_char_len": [100, 100, 100, 100],
        "jd_word_count": [10, 10, 10, 10],
        "length_ratio": [1.0, 1.0, 1.0, 1.0]
    })
    y_train = pd.Series(["Good Fit", "No Fit", "Good Fit", "No Fit"])
    
    model = train_baseline_model(X_train, y_train, model_type="logistic_regression")
    assert hasattr(model, "predict")
    
    preds = model.predict(X_train)
    assert len(preds) == 4
