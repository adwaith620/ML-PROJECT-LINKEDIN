import pytest
import pandas as pd
import numpy as np

from src.preprocessing.text_cleaner import (
    clean_text,
    extract_text_statistics,
    detect_and_flag_duplicates
)

def test_null_handling():
    assert clean_text(None) == ""
    assert clean_text(np.nan) == ""
    assert clean_text("") == ""
    assert clean_text(float('nan')) == ""

def test_whitespace_normalization():
    text = "This   is\t a test\n\nwith   many   spaces."
    cleaned = clean_text(text)
    assert cleaned == "This is a test with many spaces."

def test_unicode_normalization():
    # \u201c and \u201d are curly quotes
    text = "\u201cHello\u201d \u2013 world"
    cleaned = clean_text(text)
    # NFKD normalizes curly quotes and en-dash to ascii equivalents or similar
    # The quotes usually get kept or normalized. 
    # Let's test standard unicode handling doesn't break normal text.
    assert "Hello" in cleaned
    assert "world" in cleaned

def test_repeated_punctuation():
    text = "Section header --- and then some text *** and more === and ... and !!!"
    cleaned = clean_text(text)
    # ---, ***, === should be replaced by a space
    assert "---" not in cleaned
    assert "***" not in cleaned
    assert "===" not in cleaned
    # ... and !!! should be shortened
    assert "..." not in cleaned
    assert ".." not in cleaned
    assert "." in cleaned
    assert "!" in cleaned
    assert "!!!" not in cleaned

def test_technical_terms_preservation():
    tech_text = "Proficient in C++, C#, .NET, Node.js, React.js, Python 3, AWS, GCP, CI/CD, SQL."
    cleaned = clean_text(tech_text)
    
    assert "C++" in cleaned
    assert "C#" in cleaned
    assert ".NET" in cleaned
    assert "Node.js" in cleaned
    assert "React.js" in cleaned
    assert "CI/CD" in cleaned
    
def test_text_statistics():
    text = "Hello world this is a test"
    stats = extract_text_statistics(text)
    assert stats["word_count"] == 6
    assert stats["text_length"] == len(text)
    
    empty_stats = extract_text_statistics("")
    assert empty_stats["word_count"] == 0
    assert empty_stats["text_length"] == 0

def test_duplicate_detection():
    data = {
        "id": [1, 2, 3, 4],
        "text": [
            "This is a unique resume.",
            "This is a DUPLICATE resume.",
            "this is a duplicate resume.",  # Should be caught (case/space insensitive)
            "Another unique one."
        ]
    }
    df = pd.DataFrame(data)
    
    flagged_df = detect_and_flag_duplicates(df, "text")
    
    # 1 and 4 should be ""
    assert flagged_df.loc[0, "duplicate_group"] == ""
    assert flagged_df.loc[3, "duplicate_group"] == ""
    
    # 2 and 3 should share the same group ID and not be ""
    grp2 = flagged_df.loc[1, "duplicate_group"]
    grp3 = flagged_df.loc[2, "duplicate_group"]
    assert grp2 != ""
    assert grp2 == grp3
