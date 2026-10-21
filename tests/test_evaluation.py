import pytest
import pandas as pd
from src.evaluation.metrics import calculate_classification_metrics, get_confusion_matrix
from src.evaluation.model_comparison import compare_models
from src.evaluation.error_analysis import identify_errors
from src.evaluation.explainability import generate_candidate_explanation
from src.evaluation.leakage import check_data_leakage

def test_calculate_classification_metrics():
    y_true = ["Good Fit", "No Fit", "No Fit", "Potential Fit"]
    y_pred = ["Good Fit", "No Fit", "Potential Fit", "Potential Fit"]
    
    metrics = calculate_classification_metrics(y_true, y_pred)
    assert metrics["Accuracy"] == 0.75
    assert "Macro F1" in metrics
    assert "Good Fit F1" in metrics

def test_confusion_matrix():
    y_true = ["Good Fit", "No Fit"]
    y_pred = ["No Fit", "No Fit"]
    labels = ["Good Fit", "No Fit"]
    
    cm = get_confusion_matrix(y_true, y_pred, labels=labels)
    assert cm.loc["Good Fit", "No Fit"] == 1
    assert cm.loc["Good Fit", "Good Fit"] == 0
    assert cm.loc["No Fit", "No Fit"] == 1

def test_compare_models():
    y_true = ["A", "B", "A"]
    preds = {
        "Model1": ["A", "B", "A"],
        "Model2": ["B", "B", "B"]
    }
    
    df = compare_models(y_true, preds)
    assert len(df) == 2
    assert "Model" in df.columns
    assert df[df["Model"] == "Model1"]["Accuracy"].values[0] == 1.0

def test_identify_errors():
    df = pd.DataFrame({
        "true_label": ["Good Fit", "No Fit", "Good Fit", "Potential Fit"],
        "pred_label": ["No Fit", "Good Fit", "Good Fit", "No Fit"]
    })
    
    errors = identify_errors(df, "true_label", "pred_label")
    assert len(errors["False Positives"]) == 1
    assert len(errors["False Negatives"]) == 1
    assert len(errors["Potential Fit Errors"]) == 1

def test_explainability():
    data = {
        "overall_score": 85.0,
        "recommendation": "Strong Match",
        "skill_match_percentage": 100.0,
        "matched_skills": ["Python", "SQL"],
        "missing_required_skills": [],
        "score_breakdown": {
            "skill_contribution": 40.0,
            "baseline_text_contribution": 10.0,
            "semantic_text_contribution": 35.0,
            "weights_used": {"semantic_match": 0.4}
        }
    }
    
    text = generate_candidate_explanation(data)
    assert "Candidate Score: 85.0/100.0" in text
    assert "Skill Match: 100.0%" in text
    assert "- Python" in text
    assert "Strong required-skill coverage." in text
    assert "High semantic similarity" in text

def test_leakage_check():
    train = pd.DataFrame({"resume": ["text A", "text B", "text C"]})
    test = pd.DataFrame({"resume": ["text C", "text D", ""]})
    
    report = check_data_leakage(train, test, ["resume"])
    assert report["resume"] == 1
