# Skill and Entity Extraction (Phase 3) Report

## 1. Files Created/Modified
- `src/skill_extraction/skill_dictionary.py`
- `src/skill_extraction/normalization.py`
- `src/skill_extraction/rule_based.py`
- `src/skill_extraction/ner.py`
- `src/skill_extraction/extractor.py`
- `tests/test_skill_extraction.py`
- `notebooks/03_skill_extraction.ipynb`
- `docs/skill_extraction_report.md`

## 2. Extraction Methodology
The system utilizes a hybrid approach:
- **Dictionary-Based Exact Matching**: `rule_based.py` utilizes regex word boundary algorithms mapped against an extensive `skill_dictionary.py`.
- **Regex Extraction**: Used for extracting years of experience ("5+ years") and education structures.
- **Fallback NER (spaCy)**: Optionally uses `en_core_web_sm` to pull out generalized ORG and DATE entities if available. Deep learning custom NER was evaluated but deferred for initial V1 deployment due to dataset formatting challenges.

## 3. Entity Types Supported
- **Technical Skills** (Languages, Frameworks, DBs, Cloud Technologies, Tools)
- **Job Roles**
- **Education/Degrees**
- **Certifications**
- **Experience** (Years)

## 4. Normalization Strategy
A standard aliasing system is employed (`ALIAS_MAP`). When a surface form is detected (e.g., "react.js", "js"), it is mapped to a canonical identity ("React", "JavaScript"). The final object retains the canonical identity but also provides an array of the exact surface forms encountered in the text to retain explainability.

## 5. NER Dataset Findings
The dataset `yashpwr/resume-ner-training-data` was investigated. 
**Findings**: The data often features conversational JSON-style strings rather than strict, immediately parseable BIO format tokens. Using it for direct supervised NER training in Phase 3 would introduce noise, misalignment, and complexity beyond the scope of this baseline. A robust dictionary approach is currently favored.

## 6. Evaluation Methodology
Due to the absence of a perfectly aligned, clean BIO dataset matching our specific ontology (Technical Skills vs Roles vs Certifications), evaluation is performed qualitatively through manually verified test cases (unit testing) and error analysis against sample texts.

## 7. Metrics
Legitimate, mathematically rigorous precision/recall/F1 metrics cannot be generated without an unbiased ground-truth dataset that perfectly models our `skill_dictionary`. Synthetic metrics are not provided here.

## 8. Error Analysis
- **Correct extractions**: Explicit dictionary matches ("Python", "AWS") succeed natively.
- **Missed skills**: Highly niche libraries not present in the dictionary will be ignored.
- **False positives**: Common nouns overlapping with skills (e.g., "Go" as a verb) may trigger extraction. 
- **Ambiguous Terms**: "JS" might be extracted as "JavaScript" even if meant as someone's initials.

## 9. Integration with Phase 2
**INPUT:** `cleaned_resume_text` or `cleaned_job_text` (plain python strings).
**OUTPUT:** Structured JSON dictionaries matching the exact required schema (with keys for skills, roles, education, experience, etc.).
*Note: The extraction module does not perform destructive preprocessing, relying entirely on Phase 2's clean input.*

## 10. Google Colab Reproducibility
The notebook `03_skill_extraction.ipynb` is designed sequentially, installing `datasets`, `pandas`, and `spacy` in the initial cell. Since it relies on the `src/skill_extraction` modules, users must upload the `src` directory to Colab or run it locally from the repository root.

## 11. Commit Hash
*Not applicable due to `git` being unrecognized in the local environment.*

## 12. Push Status
*Not applicable due to `git` being unrecognized in the local environment.*
