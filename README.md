# Resume Screening and Skill Gap Analysis

**Project Type:** BTech Computer Science and AI Academic Project (2026–27)
**Repository:** `250529-dotcom/ML-PROJECT-LINKEDIN`

## 1. Project Objective

The objective of this project is to build a machine learning system that compares resumes with job descriptions, extracts relevant skills and information, calculates candidate-job compatibility, identifies skill gaps, and provides interpretable results.

## 2. Team Members

- Adwaith K
- Adwaith HA
- Abhinand Js
- Siya S
- Afraaz S M

## 3. Dataset Sources

The project primarily utilizes datasets hosted on Hugging Face. 

1. **EXAI-ResumeIntel**  
   [https://huggingface.co/datasets/mithinsagar/exai-resumeintel-data](https://huggingface.co/datasets/mithinsagar/exai-resumeintel-data)  
   Contains a resume dataset and a large job-posting dataset (approximately 1.62 million records in the `job_postings` configuration).

2. **Resume-Job Fit Merged v1**  
   [https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1](https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1)

3. **Resume NER Training Data**  
   [https://huggingface.co/datasets/yashpwr/resume-ner-training-data](https://huggingface.co/datasets/yashpwr/resume-ner-training-data)

*Note: Final dataset selection, preprocessing procedures, compatibility resolution, data leakage checks, and the construction of reproducible train/validation/test splits will be determined during the Dataset Engineering phase. There is no guarantee that all listed datasets will be used in the final model training.*

## 4. Project Pipeline

```text
Resume / Job Description
        |
        v
Text extraction and preprocessing
        |
        v
Information and skill extraction
        |
        v
Skill normalization
        |
        v
Semantic representation
        |
        v
Resume-Job matching
        |
        v
Feature engineering
        |
        v
Candidate-job scoring
        |
        v
Skill-gap analysis
        |
        v
Explainable results
        |
        v
Web application
```

## 5. Model Development

The project establishes simple baselines before progressing to more complex models. Model selection will be strictly based on empirical evaluation results.

Planned experimentation includes:
- TF-IDF and cosine similarity baselines
- Classical machine learning baselines where appropriate
- Sentence-BERT / sentence-transformer embeddings
- Hybrid models combining semantic and structured features
- Skill-gap analysis frameworks
- Explainability methods (e.g., LIME, SHAP) where appropriate

## 6. Project Phases

- **Phase 0 — Project Setup:** Repository structure, Git workflow, dependencies, documentation, data/model storage strategy.
- **Phase 1 — Dataset Engineering:** Inspect datasets, compare schemas, analyze missing values and duplicates, analyze labels and class distributions, check for data leakage, construct reproducible train/validation/test datasets.
- **Phase 2 — Resume NLP:** Resume parsing, text preprocessing, information extraction, skill extraction, skill normalization.
- **Phase 3 — Semantic Matching:** Implement baseline matching, generate sentence embeddings, evaluate semantic similarity, compare baseline and transformer-based approaches.
- **Phase 4 — Scoring and Explainability:** Feature engineering, candidate-job scoring, skill-gap detection, explainable results, model evaluation.
- **Phase 5 — Application:** Backend API, frontend interface, resume upload, job-description input, result visualization.
- **Phase 6 — Integration:** Connect model to backend, connect backend to frontend, end-to-end testing.
- **Phase 7 — Final Evaluation:** Evaluate on an untouched test set, compare model variants, analyze failure cases, document limitations, prepare final report and presentation.

## 7. Repository Structure

```text
ML-PROJECT-LINKEDIN/
│
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── .gitignore                # Ignored files (data, models, envs)
│
├── data/                     # Local data directory (contents ignored by Git)
│   └── README.md             # Data access instructions
│
├── notebooks/                # Jupyter notebooks for EDA and prototyping
│
├── src/                      # Core source code modules
│   ├── preprocessing/        # Data cleaning and text formatting
│   ├── resume_parser/        # Parsing logic for various document types
│   ├── skill_extraction/     # NER and rule-based skill identification
│   ├── matching/             # Semantic embedding and similarity logic
│   ├── scoring/              # Overall fit calculation algorithms
│   ├── explainability/       # Interpretability modules for model decisions
│   └── evaluation/           # Testing metrics and benchmark scripts
│
├── models/                   # Local model storage (contents ignored by Git)
│   └── README.md             # Model access instructions
│
├── backend/                  # API server implementation
├── frontend/                 # Web interface implementation
├── tests/                    # Unit and integration tests
└── docs/                     # Additional project documentation
```

## 8. Data and Model Storage

- GitHub stores only source code, Jupyter notebooks, documentation, and configuration files.
- Large raw datasets **must not** be committed to GitHub.
- Large model weights **must not** be committed to GitHub.
- Hugging Face or other appropriate external storage will be used to host and retrieve large datasets and model artifacts.
- The EXAI-ResumeIntel job-posting corpus is extremely large (~1.62 million records) and should be accessed programmatically rather than downloaded completely into the local repository.

## 9. Collaboration Workflow

The project utilizes a feature-branch Git workflow based off the `main` branch:

```text
main
 ├── feature/dataset-engineering
 ├── feature/resume-nlp
 ├── feature/semantic-matching
 ├── feature/scoring-xai
 └── feature/platform
```

Team members must:
1. Work on appropriate feature branches.
2. Commit changes logically.
3. Push branches to GitHub.
4. Open Pull Requests (PRs) to merge reviewed work into `main`.

## 10. Local Setup

Instructions for setting up the environment on Windows:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/250529-dotcom/ML-PROJECT-LINKEDIN.git
   cd ML-PROJECT-LINKEDIN
   ```

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment (Windows):**
   ```bash
   .\venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 11. Current Status

- **Phase 0 — Project Setup:** Complete
- **Phase 1 — Dataset Engineering:** Next
