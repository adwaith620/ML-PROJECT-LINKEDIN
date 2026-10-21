import pandas as pd
from typing import Dict, Any, List
from .metrics import calculate_classification_metrics

def compare_models(y_true: List[str], models_predictions: Dict[str, List[str]], labels: List[str] = None) -> pd.DataFrame:
    """
    Given true labels and a dictionary of {model_name: predictions},
    generates a DataFrame comparing their classification metrics.
    """
    results = []
    
    for model_name, y_pred in models_predictions.items():
        metrics = calculate_classification_metrics(y_true, y_pred, labels=labels)
        metrics["Model"] = model_name
        results.append(metrics)
        
    df = pd.DataFrame(results)
    # Reorder so Model is first
    cols = ["Model"] + [c for c in df.columns if c != "Model"]
    return df[cols]
