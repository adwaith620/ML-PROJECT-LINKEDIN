"""
Dataset utility functions for the Resume Screening and Skill Gap Analysis project.

Provides reusable preprocessing, validation, and analysis functions
used across notebooks and source modules.
"""

import re
import hashlib
from collections import Counter
from typing import Optional

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def normalise_whitespace(text: str) -> str:
    """Collapse all whitespace sequences (including newlines) into single spaces and strip."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str, lowercase: bool = False) -> str:
    """Basic text cleaning: normalise whitespace and optionally lower-case."""
    cleaned = normalise_whitespace(text)
    if lowercase:
        cleaned = cleaned.lower()
    return cleaned


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"<[^>]+>", " ", text)


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"https?://\S+|www\.\S+", "", text)


# ---------------------------------------------------------------------------
# Missing-value helpers
# ---------------------------------------------------------------------------

def missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame summarising missing values per column.

    Columns: column, missing_count, missing_pct, dtype
    """
    total = len(df)
    records = []
    for col in df.columns:
        missing = df[col].isna().sum()
        records.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "missing_count": int(missing),
            "missing_pct": round(100.0 * missing / total, 2) if total > 0 else 0.0,
        })
    return pd.DataFrame(records)


def empty_string_summary(df: pd.DataFrame, text_columns: list[str]) -> pd.DataFrame:
    """Count empty or whitespace-only strings in specified text columns."""
    total = len(df)
    records = []
    for col in text_columns:
        if col not in df.columns:
            continue
        empty_count = df[col].apply(
            lambda x: isinstance(x, str) and x.strip() == ""
        ).sum()
        records.append({
            "column": col,
            "empty_string_count": int(empty_count),
            "empty_string_pct": round(100.0 * empty_count / total, 2) if total > 0 else 0.0,
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Text length statistics
# ---------------------------------------------------------------------------

def text_length_stats(series: pd.Series, name: Optional[str] = None) -> dict:
    """Compute character-length statistics for a text Series."""
    lengths = series.dropna().astype(str).str.len()
    stats = {
        "column": name or series.name,
        "count": int(lengths.count()),
        "mean_len": round(lengths.mean(), 1) if len(lengths) > 0 else 0,
        "median_len": round(lengths.median(), 1) if len(lengths) > 0 else 0,
        "min_len": int(lengths.min()) if len(lengths) > 0 else 0,
        "max_len": int(lengths.max()) if len(lengths) > 0 else 0,
        "std_len": round(lengths.std(), 1) if len(lengths) > 0 else 0,
        "pct_under_50": round(100.0 * (lengths < 50).sum() / len(lengths), 2) if len(lengths) > 0 else 0,
        "pct_over_5000": round(100.0 * (lengths > 5000).sum() / len(lengths), 2) if len(lengths) > 0 else 0,
    }
    return stats


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def text_hash(text: str) -> str:
    """SHA-256 hash of normalised text for duplicate detection."""
    normalised = normalise_whitespace(str(text)).lower()
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def find_exact_duplicates(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """Identify exact duplicate texts (after whitespace normalisation and lower-casing).

    Returns a DataFrame with columns: hash, count, first_index
    Only rows with count > 1 are returned.
    """
    hashes = df[text_column].apply(text_hash)
    counts = hashes.value_counts()
    duplicated = counts[counts > 1]
    if len(duplicated) == 0:
        return pd.DataFrame(columns=["hash", "count", "first_index"])

    hash_to_first = {}
    for idx, h in hashes.items():
        if h not in hash_to_first:
            hash_to_first[h] = idx

    records = []
    for h, c in duplicated.items():
        records.append({
            "hash": h,
            "count": int(c),
            "first_index": hash_to_first[h],
        })
    return pd.DataFrame(records).sort_values("count", ascending=False).reset_index(drop=True)


def duplicate_summary(df: pd.DataFrame, text_column: str) -> dict:
    """High-level duplicate summary for a text column."""
    total = len(df)
    dups = find_exact_duplicates(df, text_column)
    n_groups = len(dups)
    n_duplicate_rows = int(dups["count"].sum() - n_groups) if n_groups > 0 else 0
    return {
        "column": text_column,
        "total_rows": total,
        "unique_texts": total - n_duplicate_rows,
        "duplicate_groups": n_groups,
        "duplicate_rows": n_duplicate_rows,
        "duplicate_pct": round(100.0 * n_duplicate_rows / total, 2) if total > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(df: pd.DataFrame, expected_columns: list[str]) -> dict:
    """Check whether a DataFrame contains expected columns.

    Returns a dict with: present, missing, extra
    """
    actual = set(df.columns)
    expected = set(expected_columns)
    return {
        "present": sorted(actual & expected),
        "missing": sorted(expected - actual),
        "extra": sorted(actual - expected),
    }


# ---------------------------------------------------------------------------
# Label / category analysis
# ---------------------------------------------------------------------------

def label_distribution(series: pd.Series, name: Optional[str] = None) -> pd.DataFrame:
    """Return value counts and percentages for a categorical Series."""
    counts = series.value_counts(dropna=False)
    total = counts.sum()
    dist = pd.DataFrame({
        "label": counts.index.astype(str),
        "count": counts.values,
        "pct": (100.0 * counts.values / total).round(2),
    })
    dist.attrs["column_name"] = name or series.name
    return dist


def class_imbalance_ratio(series: pd.Series) -> float:
    """Ratio of most-frequent to least-frequent class."""
    counts = series.value_counts(dropna=True)
    if len(counts) < 2:
        return float("inf")
    return round(counts.iloc[0] / counts.iloc[-1], 2)


# ---------------------------------------------------------------------------
# Streaming / sampling helpers
# ---------------------------------------------------------------------------

def sample_from_streaming_dataset(dataset_iter, n: int = 1000, seed: int = 42) -> list[dict]:
    """Take the first *n* records from a Hugging Face streaming dataset iterator.

    This is deterministic if the underlying dataset order is fixed.
    """
    records = []
    for i, record in enumerate(dataset_iter):
        if i >= n:
            break
        records.append(record)
    return records


# ---------------------------------------------------------------------------
# Leakage helpers
# ---------------------------------------------------------------------------

def check_overlap(set_a: set, set_b: set, label_a: str = "A", label_b: str = "B") -> dict:
    """Check overlap between two sets (e.g., text hashes from train and test)."""
    overlap = set_a & set_b
    return {
        f"{label_a}_size": len(set_a),
        f"{label_b}_size": len(set_b),
        "overlap_count": len(overlap),
        "overlap_pct_of_A": round(100.0 * len(overlap) / len(set_a), 2) if len(set_a) > 0 else 0.0,
        "overlap_pct_of_B": round(100.0 * len(overlap) / len(set_b), 2) if len(set_b) > 0 else 0.0,
    }
