import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from typing import Dict, Any, List

def calculate_classification_metrics(y_true: List[str], y_pred: List[str], labels: List[str] = None) -> Dict[str, Any]:
    """
    Calculate primary classification metrics (Accuracy, Macro F1, Precision, Recall).
    Useful for comparing classical baseline vs. Sentence-BERT classifiers.
    """
    if not labels:
        labels = sorted(list(set(y_true).union(set(y_pred))))
        
    metrics = {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Macro F1": f1_score(y_true, y_pred, average='macro', zero_division=0),
        "Macro Precision": precision_score(y_true, y_pred, average='macro', zero_division=0),
        "Macro Recall": recall_score(y_true, y_pred, average='macro', zero_division=0)
    }
    
    # Per-class metrics
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    
    for label in labels:
        if label in report:
            metrics[f"{label} F1"] = report[label]['f1-score']
            
    return metrics

def get_confusion_matrix(y_true: List[str], y_pred: List[str], labels: List[str] = None) -> pd.DataFrame:
    """
    Returns a confusion matrix as a Pandas DataFrame for easy plotting/inspection.
    """
    if not labels:
        labels = sorted(list(set(y_true).union(set(y_pred))))
        
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    df_cm = pd.DataFrame(cm, index=labels, columns=labels)
    return df_cm
