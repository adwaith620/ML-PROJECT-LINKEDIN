"""
normalization.py

Provides functions to normalize skills to their canonical forms.
"""

from .skill_dictionary import ALIAS_MAP, get_all_skills

# Build a fallback map from all canonical skills mapped to themselves (lowercase)
CANONICAL_LOWER_MAP = {skill.lower(): skill for skill in get_all_skills()}

def normalize_skill(surface_form: str) -> dict:
    """
    Normalizes a single skill string to its canonical form.
    Returns a dictionary with the canonical name and original surface form.
    
    If the skill is not in the alias map or canonical list, 
    it returns the surface form as the canonical name.
    """
    if not surface_form or not isinstance(surface_form, str):
        return None
        
    cleaned_form = surface_form.strip().lower()
    
    # 1. Check direct alias
    if cleaned_form in ALIAS_MAP:
        canonical = ALIAS_MAP[cleaned_form]
    # 2. Check if it matches a canonical skill in lowercase
    elif cleaned_form in CANONICAL_LOWER_MAP:
        canonical = CANONICAL_LOWER_MAP[cleaned_form]
    # 3. Fallback to original (capitalized properly if single word, or just original)
    else:
        # Simple heuristic: if it's already capitalized somehow, keep it. 
        # Else title case it as a best effort.
        if surface_form.islower() and len(surface_form) > 2:
            canonical = surface_form.title()
        else:
            canonical = surface_form.strip()
            
    return {
        "canonical": canonical,
        "surface_forms": [surface_form.strip()]
    }

def normalize_skill_list(skills: list) -> list:
    """
    Normalizes a list of skills and merges surface forms for identical canonical skills.
    Returns a list of dictionaries.
    """
    normalized_dict = {}
    
    for skill in skills:
        norm = normalize_skill(skill)
        if not norm:
            continue
            
        canonical = norm["canonical"]
        surface_form = norm["surface_forms"][0]
        
        if canonical in normalized_dict:
            if surface_form not in normalized_dict[canonical]["surface_forms"]:
                normalized_dict[canonical]["surface_forms"].append(surface_form)
        else:
            normalized_dict[canonical] = {
                "canonical": canonical,
                "surface_forms": [surface_form]
            }
            
    return list(normalized_dict.values())
