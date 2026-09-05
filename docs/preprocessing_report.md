# Phase 2: Resume & Job Description Preprocessing

## 1. Objective
The objective of Phase 2 is to build a robust, reproducible preprocessing pipeline that takes raw resumes and job descriptions and produces clean, standardized text fields. This pipeline prepares data for downstream extraction, semantic matching, and model training without destroying semantic value or causing data leakage.

## 2. Input Datasets
This pipeline utilizes the datasets analyzed in Phase 1:
- **Primary:** `Resume-Job Fit Merged v1` (Supervised Resume-JD pairs)
- **Additional (Resumes):** `EXAI-ResumeIntel` (`resumes` config)
- **Additional (Job Postings):** `EXAI-ResumeIntel` (`job_postings` config)

Raw data is loaded programmatically via Hugging Face APIs. Streaming is utilized for the 1.62M job posting corpus to manage memory footprints efficiently.

## 3. Preprocessing Pipeline
The central text-cleaning pipeline (`src/preprocessing/text_cleaner.py`) performs the following steps sequentially:
1. **Null Handling:** Casts NaNs, `None`, and missing fields to empty strings.
2. **Unicode Normalization:** NFKD normalization to standardize special characters, followed by the removal of non-printable control characters.
3. **Artifact Removal:** Removes structural bullet characters and normalizes repeated punctuation (e.g., `***`, `===`).
4. **Whitespace Normalization:** Replaces all newlines, tabs, and multiple spaces with a single standard space.
5. **Technical Preservation:** Ensures that non-alphanumeric characters embedded in technical terminology are preserved.

## 4. Resume Preprocessing
Resume text is passed through the standard text cleaner. 
- Generated fields: `cleaned_resume_text`, `resume_text_length`, `resume_word_count`.
- Metadata such as `resume_domain` or `Category` is explicitly carried over into the processed schema without being merged into the text body, avoiding label leakage.

## 5. Job-Description Preprocessing
Job descriptions undergo the same cleaning logic to ensure text symmetry between resumes and JDs (critical for Sentence-BERT matching).
- Generated fields: `cleaned_job_text`, `job_text_length`, `job_word_count`.
- Job titles and domains are preserved as distinct fields.

## 6. Technical-Token Preservation
A standard regex approach (e.g., replacing all punctuation with spaces) destroys critical technical terminology in the IT domain. Our pipeline avoids stripping standard punctuation indiscriminately.
- **Preserved examples:** `C++`, `C#`, `.NET`, `Node.js`, `React.js`, `CI/CD`.
- By specifically targeting *repeated* punctuation (`...`, `---`) and *control characters*, we clean the text while keeping software and technology names entirely intact.

## 7. Duplicate Handling
Instead of silently dropping rows—which could disrupt dataset indices or cause unaligned JD-resume pairs—exact duplicates are flagged.
- The `detect_and_flag_duplicates` function assigns a consistent hash-based `duplicate_group` ID to duplicate entries.
- Downstream tasks can use this ID to drop duplicates safely or ensure duplicate pairs fall strictly within the same train/test split.

## 8. Leakage Considerations
- **No Global Fitting:** The preprocessing pipeline is completely deterministic and stateless. No IDF calculations, vocabulary building, or global frequency filtering are performed here, eliminating any risk of test-set leakage.
- **Label Isolation:** Preprocessing acts purely on the text columns (`resume`, `jd`). Fit labels and domains are kept isolated and are not used to inform text cleaning.

## 9. Output Schema
Processed records follow a standardized schema.

**Resume Record:**
- `raw_text`: Original unedited text
- `cleaned_resume_text`: Cleaned text ready for embeddings/extraction
- `resume_word_count`: Integer word count
- `resume_text_length`: Integer character length
- `resume_domain` / `Category`: Optional string (if available in source)
- `duplicate_group`: String (empty if unique)

**Job Record:**
- `raw_text`: Original unedited text
- `cleaned_job_text`: Cleaned text ready for embeddings/extraction
- `job_word_count`: Integer word count
- `job_text_length`: Integer character length
- `jd_domain` / `Role`: Optional string (if available in source)
- `duplicate_group`: String (empty if unique)

## 10. Limitations
- **Language Bias:** The cleaning pipeline assumes English-centric unicode behavior.
- **Embedded Structures:** Tables or multi-column lists in resumes are flattened into single spaces, which removes their visual hierarchy. 
- **Spelling:** Typographical errors in resumes are not corrected at this phase, as aggressive autocorrect often corrupts technical acronyms.

## 11. Interface for Phase 3
Phase 3 (Model Training/Extraction) must interface with Phase 2 directly through the generated schemas. 
- **Primary ingestion fields:** Phase 3 models must ingest `cleaned_resume_text` and `cleaned_job_text`. Do not use `raw_text`.
- **Data Types:** Both fields are guaranteed to be standard Python `str` (no nulls, NaNs, or Floats).
- **Missing Values:** If a resume is entirely blank, `cleaned_resume_text` will be an empty string `""`. Phase 3 should filter out empty strings before passing them to Sentence-BERT.
- **Extensibility:** The Python functions `preprocess_resume_record` and `preprocess_job_record` are available in `src.preprocessing.text_cleaner` for on-the-fly inference.
