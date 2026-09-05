# Dataset Engineering Report

## 1. Objective
The objective of Phase 1 is to identify, acquire, analyze, and evaluate datasets suitable for the "Resume Screening and Skill Gap Analysis" BTech CS/AI project. This involves verifying dataset schemas, distributions, potential issues such as data leakage or class imbalance, and defining their specific roles in downstream tasks like resume parsing, job-fit matching, and skill extraction.

## 2. Dataset Sources

| Dataset Name | Source URL | Configurations / Splits |
|---|---|---|
| EXAI-ResumeIntel | [mithinsagar/exai-resumeintel-data](https://huggingface.co/datasets/mithinsagar/exai-resumeintel-data) | Configs: `resumes`, `job_postings` |
| Resume-Job Fit Merged v1 | [med2425/resume-job-fit-merged-v1](https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1) | Splits: `train`, `test` |
| Resume NER Training Data | [yashpwr/resume-ner-training-data](https://huggingface.co/datasets/yashpwr/resume-ner-training-data) | Splits: `train` |

## 3. Dataset Overview

*   **EXAI-ResumeIntel (Resumes):** Contains categorized resumes represented as extracted/processed keyword features rather than full sentences. Features 24 roughly balanced job categories.
*   **EXAI-ResumeIntel (Job Postings):** A massive corpus (approx. 1.62 million records) of job descriptions with structured text including roles, experience ranges, titles, degrees, skills, responsibilities, and salary information.
*   **Resume-Job Fit Merged v1:** A dataset explicitly constructed for resume-job matching, providing full-text resumes and job descriptions along with 3-class fit labels (No Fit, Potential Fit, Good Fit). Labels appear to be synthetically generated.
*   **Resume NER Training Data:** Formatted as chat conversations (system/user/assistant), this dataset contains named entity recognition (NER) data for resumes, though not in traditional BIO-tagging format.

## 4. Verified Dataset Statistics

| Dataset | Configuration/Split | Rows | Columns | Notes |
|---|---|---|---|---|
| EXAI-ResumeIntel | `resumes` | 2,484 | 3 | ID (int64), Category (str), Feature (str) |
| EXAI-ResumeIntel | `job_postings` | ~1.62M | 2 | **\*Statistics derived from a 2,000-record sample** |
| Resume-Job Fit Merged v1 | `train` | 80,017 | 6 | 12 resume domains, 11 JD domains |
| Resume-Job Fit Merged v1 | `test` | 13,716 | 6 | |
| Resume NER Training Data | `train` | 22,855 | 1 | |

## 5. Schema Comparison

| Dataset | Config | Rows | Columns | Resume Text | Job Text | Skills | Labels | Potential Task |
|---|---|---|---|---|---|---|---|---|
| EXAI-ResumeIntel | `resumes` | 2,484 | 3 | Yes (Keywords) | No | Implicit in text | Category | Classification |
| EXAI-ResumeIntel | `job_postings`| ~1.62M | 2 | No | Yes (Structured)| Implicit in text | Role | JD Retrieval/Analysis |
| Resume-Job Fit | Merged v1 | 93,733 | 6 | Yes (Full) | Yes (Full) | No | 3-class Fit | Matching/Scoring |
| Resume NER | Training Data | 22,855 | 1 | Yes (Chat format)| No | As Entities | As Entities | Information Extraction|

## 6. Data Quality
*   **EXAI-ResumeIntel (Resumes):** High quality with unique IDs for all 2,484 rows. Only a single missing value detected in the text features (0.04%). Note that text consists of keywords rather than natural language.
*   **EXAI-ResumeIntel (Job Postings):** Features structured fields concatenated into text. Sample analysis indicates 373 unique roles across 2,000 sampled rows.
*   **Resume-Job Fit Merged v1:** Complete data with zero missing values across all splits. Contains full-text fields.
*   **Resume NER Training Data:** Data is nested in JSON-like lists (`messages`). Requires custom parsing to extract training signals.

## 7. Missing Values

| Dataset | Configuration | Column | Missing Count | Missing % |
|---|---|---|---|---|
| EXAI-ResumeIntel | `resumes` | `Feature` | 1 | 0.04% |
| Resume-Job Fit Merged v1 | `train` / `test` | All | 0 | 0.00% |
| Resume NER Training Data | `train` | All | 0 | 0.00% |

*(Note: EXAI Job Postings full missing value analysis not performed due to scale.)*

## 8. Duplicate Analysis
*   **EXAI-ResumeIntel (Resumes):** Checked on the `ID` column; 2,484 unique values found (no duplicates).
*   **EXAI-ResumeIntel (Job Postings):** Full duplicate analysis for the 1.62M dataset was not performed due to hardware/memory constraints. Sample-based streaming was utilized.
*   **Resume-Job Fit Merged v1:** No explicit duplicate analysis performed yet, but cross-split duplication should be verified prior to modeling.

## 9. Label Analysis
*   **Resume-Job Fit Merged v1 (`train` split labels):**
    *   No Fit: 60,313 (75.38%)
    *   Potential Fit: 13,907 (17.38%)
    *   Good Fit: 5,797 (7.24%)
    *   *Note: High class imbalance ratio of 10.4 between majority and minority classes.*
*   **EXAI-ResumeIntel (Resumes):**
    *   24 distinct categories.
    *   Categories are roughly balanced, ranging from 22 to 120 samples per category.
    *   Imbalance ratio is 5.45.

## 10. Data Leakage Analysis
*   **Resume-Job Fit Merged v1:** High Risk. The `source='generated_smart'` metadata suggests labels may be synthetically generated. If the labels are deterministically derived from `resume_domain` and `jd_domain` overlap, models might learn to map domains rather than understanding semantic text fit. *Recommendation:* Analyze correlation between domain overlap and labels.
*   **EXAI Datasets:** Low Risk. The `resumes` and `job_postings` are maintained in separate configurations without explicit linking keys. Cross-contamination risk is low but must be verified if building synthetic matching pairs.
*   **Resume NER Training Data:** Low Risk. Single-purpose dataset with minimal overlap risk.

## 11. Dataset Suitability

| Dataset | Resume Parsing | Skill Extraction | Resume-JD Matching | Scoring/Evaluation |
|---|---|---|---|---|
| EXAI-ResumeIntel | No (Pre-parsed) | Partial (Keywords) | No | No |
| Resume-Job Fit | Yes | Yes (Implicit) | Yes | Yes |
| Resume NER Data | Yes | Yes | No | No |

## 12. Recommended Dataset Roles
*   **Resume-Job Fit Merged v1:** **PRIMARY** dataset for supervised resume-JD matching tasks due to the presence of explicit fitness labels. Must be used with caution given the synthetic origin of the labels.
*   **EXAI-ResumeIntel (Resumes):** Useful for category-level resume classification and acting as an independent resume text source.
*   **EXAI-ResumeIntel (Job Postings):** Serves as a large-scale job description corpus for retrieval and semantic analysis tasks. Too large for full supervised training iterations without sampling.
*   **Resume NER Training Data:** Potential resource for fine-tuning resume information extraction models, provided the chat format can be accurately parsed into usable target formats.

## 13. Train / Validation / Test Strategy
*   **Resume-Job Fit Merged v1:**
    *   Utilize the existing 80,017 `train` split to create a new internal validation set.
    *   Stratify splits by the `label` and `domain` columns to handle the 10.4 imbalance ratio.
    *   Perform rigorous checks for duplicate resumes/JDs leaking across the train and test splits.
    *   Keep the provided 13,716 `test` split strictly untouched for final model evaluation.
*   **EXAI Datasets:** Use primarily for unsupervised tasks, pre-training, or as external knowledge bases. No supervised matching splits required.

## 14. Large Dataset Handling Strategy
*   **Streaming:** Use Hugging Face streaming APIs to interact with the 1.62M EXAI job postings, circumventing the need to load the entire corpus into memory.
*   **Sampling:** For iterative experiments, rely on reproducible, fixed-seed random samples (e.g., 10K-50K records).
*   **Full Corpus:** Reserve operations on the full corpus solely for final retrieval-based indexing or evaluation tasks where necessary.
*   **Memory and Reproducibility:** Streaming avoids overwhelming system memory. Ensure random seeds are fixed for all sampling logic to guarantee reproducibility across experiments.

## 15. Limitations
*   Labels in Resume-Job Fit are synthetically generated, not human-annotated, potentially introducing generation artifacts or bias.
*   The NER dataset utilizes a conversational format rather than standard BIO tagging, requiring a complex pre-processing step.
*   EXAI resumes are already pre-processed into keywords, limiting their utility for natural language understanding tasks.
*   Statistical profiling of the massive EXAI job postings dataset relies on sample-based estimation rather than full-table scans.
*   None of the evaluated datasets contain explicit, ground-truth annotations for granular skill extraction.

## 16. Recommendation for Phase 2
*   Begin modeling by establishing baseline matching experiments using the Resume-Job Fit dataset.
*   Develop a parsing script to convert the conversational NER data into standard extraction formats to assess data quality.
*   Design and execute a small-scale manual annotation study to validate the reliability of the synthetic labels in Resume-Job Fit.
*   Build a robust preprocessing pipeline for raw resume text cleaning, as the existing data varies significantly in structure and quality.
