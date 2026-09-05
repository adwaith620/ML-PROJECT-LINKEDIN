"""
ner.py

Optional NER-based extraction module.
Uses spaCy (if available) to extract generic entities like ORG, GPE, and DATE 
which might support extracting unrecognized degrees or organizations.

In a full production system, a specialized model trained on resume NER 
data could be injected here.
"""

import logging

logger = logging.getLogger(__name__)

try:
    import spacy
    # Load the small English model. If not available, we fail gracefully.
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    logger.warning("spaCy or 'en_core_web_sm' model not found. NER extraction will be disabled.")

def extract_entities_ner(text: str) -> dict:
    """
    Extracts entities using a standard NER model.
    Returns a dictionary of entity types (e.g., 'ORG', 'DATE') to lists of extracted strings.
    """
    entities = {
        "ORG": [],
        "DATE": [],
        "GPE": [],
        "PERSON": []
    }
    
    if not SPACY_AVAILABLE or not text:
        return entities
        
    doc = nlp(text)
    
    for ent in doc.ents:
        if ent.label_ in entities:
            # Add unique strings only, preserving case of first appearance
            surface = ent.text.strip()
            if surface.lower() not in [e.lower() for e in entities[ent.label_]]:
                entities[ent.label_].append(surface)
                
    return entities
