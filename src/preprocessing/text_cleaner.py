"""
Text Cleaner utility module for Resume and Job Description preprocessing.

This module provides reusable functions for cleaning text while preserving
important technical tokens (like C++, C#, .NET, Node.js, etc.).
"""

import re
import unicodedata
import pandas as pd
from typing import Optional, Dict, Any, Union


def handle_nulls(text: Any) -> str:
    """Handle null or non-string values."""
    if pd.isna(text) or text is None:
        return ""
    return str(text)


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters to NFKD and remove non-printable control chars."""
    if not text:
        return ""
    # Normalize unicode (e.g. converting special quotes/hyphens to ascii if possible)
    normalized = unicodedata.normalize("NFKD", text)
    # Remove control characters except standard whitespace (\t, \n, \r)
    # Control chars are categorized as 'C' in Unicode category
    normalized = "".join(
        ch for ch in normalized if unicodedata.category(ch)[0] != "C" or ch in ("\t", "\n", "\r")
    )
    return normalized


def normalize_formatting_and_punctuation(text: str) -> str:
    """
    Remove obvious formatting artifacts and normalize repeated punctuation 
    while preserving technical terms.
    """
    # Replace common bullet points with standard space or dash
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\xb7]', ' ', text)
    
    # Normalize repeated punctuation (e.g., ***, ---, ===) to a single space
    # but be careful not to break technical terms like "C++" (handled by looking for 3+ repetitions)
    text = re.sub(r'([*=\-_~]){3,}', ' ', text)
    
    # Normalize repeated standard punctuation like ..., !!!, ??? to a single mark
    text = re.sub(r'\.{3,}', '.', text)
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    
    return text


def normalize_whitespace(text: str) -> str:
    """Normalize line-breaks and multiple spaces to a single space."""
    # Replace all whitespace characters (newlines, tabs, spaces) with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def clean_text(text: Any, lowercase: bool = False) -> str:
    """
    Apply full cleaning pipeline to a single text string.
    
    Preserves:
    - programming languages (C++, C#, .NET)
    - technologies (Node.js, React.js)
    - punctuation that might be part of technical terms (+, #, ., -, /)
    """
    text = handle_nulls(text)
    if not text:
        return ""
        
    text = normalize_unicode(text)
    text = normalize_formatting_and_punctuation(text)
    
    # Optional lowercasing
    if lowercase:
        text = text.lower()
        
    text = normalize_whitespace(text)
    return text


def extract_text_statistics(text: str) -> Dict[str, int]:
    """Calculate basic length and word count for a cleaned string."""
    if not text:
        return {"text_length": 0, "word_count": 0}
        
    return {
        "text_length": len(text),
        "word_count": len(text.split())
    }


def preprocess_resume_record(record: Dict[str, Any], text_column: str = "resume", id_column: Optional[str] = None) -> Dict[str, Any]:
    """
    Preprocess a single resume record.
    Returns a structured dictionary with cleaned text and statistics.
    """
    raw_text = handle_nulls(record.get(text_column, ""))
    cleaned_text = clean_text(raw_text, lowercase=False)
    stats = extract_text_statistics(cleaned_text)
    
    processed = {
        "raw_text": raw_text,
        "cleaned_resume_text": cleaned_text,
        "resume_text_length": stats["text_length"],
        "resume_word_count": stats["word_count"]
    }
    
    if id_column and id_column in record:
        processed["record_id"] = record[id_column]
        
    # Preserve category or domain if available
    for key in ["Category", "resume_domain", "domain"]:
        if key in record:
            processed[key] = record[key]
            
    return processed


def preprocess_job_record(record: Dict[str, Any], text_column: str = "jd", id_column: Optional[str] = None) -> Dict[str, Any]:
    """
    Preprocess a single job description record.
    Returns a structured dictionary with cleaned text and statistics.
    """
    raw_text = handle_nulls(record.get(text_column, ""))
    cleaned_text = clean_text(raw_text, lowercase=False)
    stats = extract_text_statistics(cleaned_text)
    
    processed = {
        "raw_text": raw_text,
        "cleaned_job_text": cleaned_text,
        "job_text_length": stats["text_length"],
        "job_word_count": stats["word_count"]
    }
    
    if id_column and id_column in record:
        processed["job_id"] = record[id_column]
        
    # Preserve role or domain if available
    for key in ["Role", "jd_domain", "title"]:
        if key in record:
            processed[key] = record[key]
            
    return processed


def detect_and_flag_duplicates(df: pd.DataFrame, text_column: str, group_id_col: str = "duplicate_group") -> pd.DataFrame:
    """
    Identifies exact duplicates in a dataframe based on the cleaned text column.
    Assigns a group ID to duplicates, preserving all records but linking them.
    """
    df = df.copy()
    
    # Ensure text column exists
    if text_column not in df.columns:
        df[group_id_col] = ""
        return df
        
    # Create a normalized version for duplicate detection (lowercase and stripped)
    norm_text = df[text_column].astype(str).str.lower().str.strip()
    
    # Find duplicates
    # keep=False marks all duplicates as True
    is_duplicate = norm_text.duplicated(keep=False)
    
    # Initialize group col with empty string
    df[group_id_col] = ""
    
    # Assign unique IDs to each duplicate group based on a hash of the normalized text
    if is_duplicate.any():
        dup_texts = norm_text[is_duplicate]
        
        import hashlib
        def get_hash(t):
            return hashlib.md5(t.encode('utf-8')).hexdigest()[:8]
            
        group_hashes = dup_texts.apply(get_hash)
        df.loc[is_duplicate, group_id_col] = group_hashes
        
    return df
