import pandas as pd
from typing import List, Dict

def identify_errors(df: pd.DataFrame, true_col: str, pred_col: str) -> Dict[str, pd.DataFrame]:
    """
    Identifies False Positives and False Negatives for qualitative error analysis.
    Assumes standard labels like "Good Fit" and "No Fit".
    """
    errors = {}
    
    # False Positives: Model said Good Fit, actually No Fit
    fp_mask = (df[true_col] == 'No Fit') & (df[pred_col] == 'Good Fit')
    errors['False Positives'] = df[fp_mask]
    
    # False Negatives: Model said No Fit, actually Good Fit
    fn_mask = (df[true_col] == 'Good Fit') & (df[pred_col] == 'No Fit')
    errors['False Negatives'] = df[fn_mask]
    
    # Confusion around Potential Fit
    potential_errors_mask = (df[true_col] != df[pred_col]) & ((df[true_col] == 'Potential Fit') | (df[pred_col] == 'Potential Fit'))
    errors['Potential Fit Errors'] = df[potential_errors_mask]
    
    return errors
