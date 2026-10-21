# Implementation Audit: Resume Screening and Skill Gap Analysis System

**Date:** 2026-10-21  
**Project:** Resume Screening and Skill Gap Analysis System using NLP and Machine Learning  
**Target Repository:** `https://github.com/adwaith620/ML-PROJECT-LINKEDIN`  
**Current Branch:** `feature/final-web-application` (based on `main` at `ea061ab`, fast-forwarded to `phase7` at `3029133`)

---

## 1. Inspected Branches and Commit Hashes

| Branch | Latest Commit Hash | Author & Date | Commit Message | Verified State / Notes |
|---|---|---|---|---|
| `origin/main` | `6d956cd` | adwaith620 (2026-09-05) | docs: update README with verified datasets and project structure | Initial setup & docs |
| `local/main` | `ea061ab` | adwaith620 (2026-09-05) | feat: implement resume and job preprocessing | Ahead of origin/main by 2 commits (same as `phase2`) |
| `origin/phase1` | `7db32a9` | adwaith620 (2026-09-05) | feat: complete phase 1 dataset engineering | Dataset utils & exploratory notebook |
| `origin/phase2` | `ea061ab` | adwaith620 (2026-09-05) | feat: implement resume and job preprocessing | Text cleaning & normalisation |
| `origin/phase3` | `38e22bd` | bone-fires (2026-09-05) | idk, completed phase3, whatever than means | Skill extraction, rule-based NER, dictionary |
| `origin/phase4` | `1b8647f` | adwaith620 (2026-09-05) | feat: implement baseline resume job matching model | Baseline feature extractor & TF-IDF matching |
| `origin/phase5` | `da24366` | bone-fires (2026-09-05) | completed phase5 | Sentence-BERT semantic matcher |
| `origin/phase6` | `9e7aebc` | adwaith620 (2026-09-05) | feat: implement candidate scoring and skill gap analysis | Candidate scoring, skill gap, ranking |
| `origin/phase7` | `3029133` | adwaith620 (2026-09-05) | feat: add model evaluation and explainability | Merged phase5 into phase7 (`c1d0e7f`), added metrics, explainability, tests |

**Commit Graph Relationship:**
- The repository previously had two parallel development tracks branched from `6d956cd`:
  - Track 1: `phase1` (`7db32a9`) -> `phase2` (`ea061ab`) -> `phase4` (`1b8647f`) -> `phase6` (`9e7aebc`)
  - Track 2: `phase3` (`38e22bd`) -> `phase5` (`da24366`)
- In `phase7`, commit `c1d0e7f` merged Track 2 (`origin/phase5`) into Track 1 (`phase6`), and commit `3029133` added evaluation and explainability on top.
- Therefore, `phase7` contains the complete combination of all phases 1 through 7.
- Integration branch `feature/final-web-application` has been created and synchronized with `3029133`.

---

## 2. Existing Modules and Responsibilities

| Directory / Module | File(s) | Primary Responsibilities | Status |
|---|---|---|---|
| `src/preprocessing` | `text_cleaner.py`, `dataset_utils.py`, `__init__.py` | Text normalization, unicode NFKD cleaning, whitespace collapsing, preservation of technical terms (`C++`, `C#`, `.NET`, `Node.js`, `React.js`). | Working & tested |
| `src/skill_extraction` | `skill_dictionary.py`, `rule_based.py`, `normalization.py`, `ner.py`, `extractor.py` | Regex dictionary matching, word boundary boundary lookups, technical skill taxonomy, canonical aliases, education/role/experience regex. | Working & tested |
| `src/matching` | `baseline.py`, `sentence_bert.py`, `__init__.py` | Classical TF-IDF feature extraction (`BaselineFeatureExtractor`), paired cosine distance, Logistic Regression / SVM models. `SemanticMatcher` with `all-MiniLM-L6-v2` Sentence-BERT embedding and cosine similarity. | Working & tested |
| `src/scoring` | `config.py`, `skill_gap.py`, `candidate_score.py`, `ranking.py`, `__init__.py` | Skill gap analysis (matched required, missing required, additional skills), configurable weighted scoring (skills + TF-IDF baseline + semantic), categorical recommendations. | Working & tested |
| `src/evaluation` | `metrics.py`, `explainability.py`, `error_analysis.py`, `leakage.py`, `model_comparison.py` | Classification metrics, textual score explanations, confusion matrices, data leakage checks. | Working & tested |
| `src/resume_parser` | `__init__.py` | Empty module placeholder. Intended for file parsing (PDF, DOCX, TXT) and document extraction. | **Missing** |
| `backend` | `.gitkeep` | Empty placeholder directory. No FastAPI / server implementation yet. | **Missing** |
| `frontend` | `.gitkeep` | Empty placeholder directory. No UI / web application yet. | **Missing** |

---

## 3. Existing Notebooks, Tests, Reports, and Model Artifacts

### 3.1 Notebooks
- `notebooks/01_dataset_exploration.ipynb`: 317 lines, 0 executed output cells (outputs cleared or unexecuted).
- `notebooks/02_resume_preprocessing.ipynb`: 910 lines, 11 executed output cells.
- `notebooks/03_skill_extraction.ipynb`: 230 lines, 0 executed output cells.
- `notebooks/04_baseline_matching.ipynb`: 979 lines, 11 executed output cells.
- `notebooks/05_sentence_bert_matching.ipynb`: 239 lines, 0 executed output cells.
- `notebooks/06_candidate_scoring_skill_gap.ipynb`: 505 lines, 6 executed output cells.
- `notebooks/07_model_evaluation_explainability.ipynb`: 5857 lines, 8 executed output cells.

### 3.2 Tests
Existing test suite executed via Python 3.11 (`python -m pytest`):
- `tests/test_preprocessing.py`: 7 passed
- `tests/test_skill_extraction.py`: 9 passed
- `tests/test_matching.py`: 3 passed
- `tests/test_sentence_bert.py`: 5 passed
- `tests/test_scoring.py`: 6 passed
- `tests/test_evaluation.py`: 6 passed
- **Total: 36 tests passed, 0 failed (43.42s).**

### 3.3 Model Artifacts
Located in `models/` (local untracked artifacts):
- `models/baseline_feature_extractor.joblib` (187 KB) — verified loadable: `BaselineFeatureExtractor` with fitted `TfidfVectorizer`.
- `models/baseline_model_lr.joblib` (1.5 KB) — verified loadable: trained `LogisticRegression` classifier.
- Pre-trained Sentence-BERT model: uses `all-MiniLM-L6-v2` via Hugging Face `sentence-transformers` cache (`~/.cache/huggingface/hub`).

### 3.4 Reports in `docs/`
- `docs/dataset_report.md`
- `docs/preprocessing_report.md`
- `docs/skill_extraction_report.md`
- `docs/baseline_model_report.md`
- `docs/sentence_bert_report.md`
- `docs/scoring_skill_gap_report.md`
- `docs/evaluation_explainability_report.md`

---

## 4. Working, Partially Working, and Missing Features

### Working
- Text cleaning and normalization preserving technical tokens.
- Rule-based skill, degree, certification, and role extraction.
- Canonical skill mapping and alias resolution (`js` -> `javascript`, `k8s` -> `kubernetes`, etc.).
- Classical TF-IDF cosine similarity feature extraction and pre-trained baseline model loading.
- Semantic matching via Sentence-BERT with document chunking.
- Skill gap analysis (matched required, missing required, additional).
- Weighted scoring system with threshold recommendations.
- Textual breakdown explanation generator.

### Partially Working
- `src/matching/sentence_bert.py` eager-loads `SentenceTransformer('all-MiniLM-L6-v2')` synchronously on class instantiation in `__init__`. Needs lazy loading and local fallback detection so web requests or imports do not block or crash if offline.
- Python environment: Python 3.11 is the environment with ML packages (`C:\Users\adwai\AppData\Local\Programs\Python\Python311\python.exe`), while the system PATH default `python` is an MSYS2 Python 3.12 binary without pip packages. Startup scripts and runner commands must explicitly invoke Python 3.11 or activate the correct environment.

### Missing Features
1. **Document Parser (`src/resume_parser`)**:
   - PDF text extraction (with page count limit and corruption handling).
   - DOCX text extraction (with XML extraction and corruption handling).
   - TXT text extraction (with multi-encoding support: UTF-8, Latin-1, CP1252).
   - Document upload limit validation (25MB resume, 10MB JD, 100 pages, 5MB extracted text).
2. **Unified Analysis Pipeline**:
   - End-to-end integration orchestrating file parsing, text cleaning, skill extraction, matching (semantic + classical fallback), scoring, and report generation.
3. **Backend API (`backend/`)**:
   - FastAPI application.
   - Endpoints: `GET /api/health`, `POST /api/analyze`, `GET /api/config`.
   - Multipart file upload handling with safe temporary file storage and deterministic cleanup.
   - Professional PDF report generation endpoint (`reportlab`).
   - JSON export.
4. **Frontend UI (`frontend/`)**:
   - React + TypeScript web application (Vite-based).
   - Drag-and-drop / file picker for resume (PDF/DOCX/TXT).
   - Text area / file upload for job description.
   - Live stage-by-stage honest progress status.
   - Compatibility score display with component breakdown.
   - Matched skills badges with evidence snippets.
   - Missing / unevidenced required skills badges.
   - Additional skills badges.
   - Extracted experience, education, certifications.
   - PDF download, JSON export, copy summary actions.
   - Reset / "Analyze another candidate" workflow.
5. **EXAI Feasibility Report (`docs/exai_feasibility_report.md`)**:
   - Evaluation of `mithinsagar/exai-resumeintel-data` and transparent non-generative alternative.

---

## 5. Conflicting Interfaces and Dependencies

- In `src/matching/baseline.py`, `BaselineFeatureExtractor.transform()` produces a DataFrame of features. It expects raw text strings.
- In `src/matching/sentence_bert.py`, `SemanticMatcher.compute_similarity()` returns a float similarity in `[-1.0, 1.0]`.
- In `src/scoring/candidate_score.py`, `calculate_candidate_score()` expects `baseline_text_score` and `semantic_score` as floats in `[0, 1]`, and `skill_match_percentage` in `[0, 100]`. If `semantic_score` is `None`, weights automatically switch to `DEFAULT_WEIGHTS_NO_SEMANTIC`.
- In `tests/test_evaluation.py` and `tests/test_scoring.py`, `sys.path.insert(0, ...)` is needed if pytest is run without `src` in pythonpath. Running via `python -m pytest` or configuring `pyproject.toml` / `pytest.ini` standardizes this.

---

## 6. Required Integration Work

1. **Build `src/resume_parser/`**:
   - Implement `parser.py` supporting PDF (via `pypdf` or `pdfminer`), DOCX (via `python-docx` or zipfile/xml), TXT.
   - Implement limit validator (`limits.py`) enforcing:
     - 25 MB max file size for resumes.
     - 10 MB max file size for job descriptions.
     - 100 max PDF pages.
     - 5 MB max extracted text (UTF-8).
2. **Build `src/pipeline.py`**:
   - Orchestrates the full lifecycle: parse document -> clean text -> extract skills/entities -> compute baseline TF-IDF cosine similarity -> compute Sentence-BERT semantic similarity -> analyze skill gaps -> calculate score & recommendation -> build structured result object.
3. **Build `backend/`**:
   - FastAPI app (`backend/main.py`), routers, schemas (`backend/schemas.py`), PDF generator (`backend/pdf_generator.py`).
   - Health check with model status.
4. **Build `frontend/`**:
   - Vite + React + TypeScript + Tailwind CSS / polished CSS.
   - Clean B2B interface without fluff.
5. **Startup Scripts**:
   - `run_local.bat` ensuring Python 3.11 and Node.js are used, launching FastAPI on port 8000 and Vite on port 5173.
6. **Documentation & Feasibility Research**:
   - `docs/scoring_methodology.md`
   - `docs/file_upload_limits.md`
   - `docs/exai_feasibility_report.md`
   - `docs/testing_report.md`
   - Updated `README.md`

---

## 7. Important Limitations

- Sentence-BERT requires downloading `all-MiniLM-L6-v2` (~90 MB) if not cached. Local fallback to TF-IDF cosine similarity must be provided if offline or if memory is constrained.
- Skill extraction is rule- and dictionary-based; it captures known skills, aliases, and explicit patterns, but may miss novel or domain-specific abbreviations not present in the taxonomy.
- Compatibility scores are decision-support heuristics, not calibrated hiring predictions or legal fitness assessments.
