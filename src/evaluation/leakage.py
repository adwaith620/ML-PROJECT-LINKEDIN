import pandas as pd
from typing import Dict, List

def check_data_leakage(train_df: pd.DataFrame, test_df: pd.DataFrame, text_columns: List[str]) -> Dict[str, int]:
    """
    Checks for exact text duplicates between train and test splits to detect data leakage.
    Returns a dictionary of counts for each column checked.
    """
    leakage_report = {}
    
    for col in text_columns:
        if col in train_df.columns and col in test_df.columns:
            train_texts = set(train_df[col].dropna().str.lower().str.strip())
            test_texts = set(test_df[col].dropna().str.lower().str.strip())
            
            # Remove empty strings
            train_texts.discard("")
            test_texts.discard("")
            
            overlap = train_texts.intersection(test_texts)
            leakage_report[col] = len(overlap)
            
    return leakage_report
