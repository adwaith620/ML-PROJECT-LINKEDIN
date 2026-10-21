# TalentLens — Resume Screening and Skill Gap Analysis System

**Project Type:** BTech Computer Science & AI Academic Project (2026–27)  
**System Name:** TalentLens  
**Repository:** `adwaith620/ML-PROJECT-LINKEDIN`  
**Current Active Branch:** `feature/final-web-application`  

---

## 1. Project Objective

TalentLens is an end-to-end recruitment decision-support system powered by Natural Language Processing (NLP) and Machine Learning. The application parses candidate resumes (PDF, DOCX, TXT), validates document integrity, cleans text while preserving specialized technical tokens (such as `C++`, `C#`, `.NET`, `CI/CD`, `Python 3`, and `SQL`), performs section-aware parsing of job descriptions, classifies skills across four precision tiers (Exact match, Recognized alias, Related skill with transferable credit, Not evidenced), extracts prioritized sentence-level evidence (preferring Work Experience and Projects over flat skills lists), and calculates transparent compatibility scores in both Light and Dark themes.

---

## 2. Team Members

- Adwaith K
- Adwaith HA
- Abhinand Js
- Siya S
- Afraaz S M

---

## 3. System Architecture & Pipeline Flow

```text
Candidate Resume (PDF/DOCX/TXT) + Job Description
                      │
                      ▼
[Phase 2 Parser] Document Validation & Size Constraints (25MB Resume / 10MB JD / 100 Pages)
                      │
                      ▼
[Phase 2 NLP] Text Cleaning & Normalization (Preserving C++, C#, .NET, Node.js, React.js)
                      │
                      ▼
[Phase 3 Extraction] Skill Taxonomy & Canonical Alias Resolution (k8s -> kubernetes)
                      │
                      ▼
[Phase 3 Evidence] Non-Fabricated Sentence Evidence Snippet Extraction from Resume
                      │
                      ▼
[Phase 4 & 5 Matching] Multi-Modal Similarity Engine:
   ├── Classical TF-IDF Cosine Distance (BaselineFeatureExtractor)
   └── Sentence-BERT all-MiniLM-L6-v2 Dense Semantic Similarity
                      │
                      ▼
[Phase 6 Scoring] Weighted Scoring & Skill Gap Analysis:
   ├── Matched Required Skills Coverage
   ├── Missing / Unevidenced Required Skills
   └── Additional Unsolicited Competencies
                      │
                      ▼
[Phase 6 UI & Export] Professional Web Application & ReportLab PDF Export
```

---

## 4. Reused & Verified Machine Learning Components

All foundational research from the project's historical phases has been integrated into the production pipeline:
- **Phase 1 (Dataset Exploration):** Research schemas and distributions documented in `docs/dataset_report.md`.
- **Phase 2 (Text Preprocessing):** Unicode NFKD normalization, whitespace control, and punctuation-safe regex in `src/preprocessing/text_cleaner.py`.
- **Phase 3 (Skill Extraction):** Entity extraction dictionary and alias resolution in `src/skill_extraction/`.
- **Phase 4 (Classical Baseline):** Pre-trained `BaselineFeatureExtractor` (`models/baseline_feature_extractor.joblib`) and TF-IDF cosine distance in `src/matching/baseline.py`.
- **Phase 5 (Sentence-BERT Matching):** Dense semantic representation using `all-MiniLM-L6-v2` with bounded document chunking in `src/matching/sentence_bert.py`.
- **Phase 6 (Scoring & Ranking):** Skill gap calculus and weighted scoring in `src/scoring/`.
- **Phase 7 (Evaluation & Transparency):** Metric calculators and non-generative score explanation templates in `src/evaluation/`.

---

## 5. Scoring Methodology

The overall compatibility score $S \in [0.0, 100.0]$ is computed as:

$$S_{\text{overall}} = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{baseline}} \cdot S_{\text{baseline}} + w_{\text{semantic}} \cdot S_{\text{semantic}}$$

### Configurable Weights
- **Sentence-BERT + Classical Hybrid (Default):**
  - Structured Skill Coverage: **40%**
  - Baseline TF-IDF Similarity: **20%**
  - Sentence-BERT Semantic Similarity: **40%**
- **Classical Baseline Fallback (Offline Mode):**
  - Structured Skill Coverage: **60%**
  - Baseline TF-IDF Similarity: **40%**
  - Semantic Similarity: **0%**

### Categorical Fit Thresholds
- **80.0% – 100.0%:** Strong Match
- **60.0% – 79.9%:** Moderate Match
- **40.0% – 59.9%:** Potential Match
- **0.0% – 39.9%:** Low Match

For complete mathematical definitions and edge-case handling, see [`docs/scoring_methodology.md`](docs/scoring_methodology.md).

---

## 6. Document Constraints & Upload Limits

Enforced continuously at the frontend, multipart HTTP handler, document parsers, and NLP text buffers:
- **Resume File Size:** Max 25 MB ($26,214,400$ bytes)
- **Job Description File Size:** Max 10 MB ($10,485,760$ bytes)
- **PDF Page Count:** Max 100 pages (verified before full text extraction)
- **Extracted Plain Text:** Max 5 MB UTF-8 text
- **Supported Formats:** PDF (`.pdf`), Microsoft Word (`.docx`), Plain Text (`.txt`)

For complete details on enforcement points, see [`docs/file_upload_limits.md`](docs/file_upload_limits.md).

---

## 7. Explainable AI (EXAI) Feasibility Research

As per architectural assessment, Explainable AI was **researched for feasibility rather than implemented as a generative subsystem**.
- Investigated resource: `mithinsagar/exai-resumeintel-data` on Hugging Face.
- **Finding:** Programmatic analysis revealed that `mithinsagar/exai-resumeintel-data` contains zero explainability ground truth, rationale labels, or paired alignment.
- **Decision:** The system implements **intrinsic, deterministic transparency**: every matched skill displays genuine sentence evidence quotes from the resume, missing skills are explicitly labeled as unevidenced, and the exact mathematical score contribution of every component is inspectable.

Read the complete 10-point research paper in [`docs/exai_feasibility_report.md`](docs/exai_feasibility_report.md).

---

## 8. Installation & Setup

### Prerequisites
- **Python 3.11+** with `pip`
- **Node.js v18+** with `npm`

### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 9. Running the Application Locally

### Method A: One-Click Windows Launch Script (Recommended)
Simply double-click or run:
```cmd
run_local.bat
```
This automatically verifies Python and Node.js versions, starts the FastAPI backend and Vite frontend, and displays the local URLs.

### Method B: Separate Services

**Terminal 1 — Backend API:**
```cmd
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend UI:**
```cmd
cd frontend
npm run dev
```

### Local Application Endpoints
- **Frontend Web UI:** [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **Backend API Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Runtime Configuration:** [http://127.0.0.1:8000/api/config](http://127.0.0.1:8000/api/config)

---

## 10. Testing & Verification

Run the full automated test suite (67 unit and integration tests):
```cmd
python -m pytest
```

### Test Suite Results (100% Passing)
```text
tests\test_api_integration.py ......                                     [  8%]
tests\test_evaluation.py ......                                          [ 17%]
tests\test_matching.py ...                                               [ 22%]
tests\test_preprocessing.py .......                                      [ 32%]
tests\test_resume_parser.py ..........                                   [ 47%]
tests\test_scoring.py ......                                             [ 56%]
tests\test_sentence_bert.py .....                                        [ 64%]
tests\test_skill_extraction.py .........                                 [ 77%]
tests\test_skill_matching_accuracy.py ...............                    [100%]

======================= 67 passed in 21.56s (100% Pass) =======================
```

Detailed test logs and boundary verification are recorded in [`docs/testing_report.md`](docs/testing_report.md).

---

## 11. Sample Inputs for Testing

Sample input files are provided in `data/sample_inputs/` for immediate verification:
- `data/sample_inputs/sample_resume_alex_rivers.txt` — Senior Backend Engineer resume with real-world work experience, projects, and skills.
- `data/sample_inputs/sample_job_senior_backend_engineer.txt` — Job posting with explicit Required Qualifications and Preferred Qualifications.

---

## 12. Privacy & Data Handling

- **Zero Permanent Storage:** Resumes, job descriptions, and extracted texts are never permanently saved to database disks.
- **Safe Memory Processing:** Documents are processed in-memory or in strictly isolated temporary buffers and discarded immediately after report generation.
- **Local Inference:** All calculations execute locally; personal identifiable information (PII) is never transmitted to external third-party AI APIs.

---

## 13. Documentation Index

- [`docs/implementation_audit.md`](docs/implementation_audit.md) — Comprehensive pre-integration audit of all project branches and commits.
- [`docs/architecture.md`](docs/architecture.md) — System specifications, component topology, and data flow.
- [`docs/scoring_methodology.md`](docs/scoring_methodology.md) — Mathematical formulas, weights, and recommendation categories.
- [`docs/file_upload_limits.md`](docs/file_upload_limits.md) — Multi-tier upload limits and DoS defense boundaries.
- [`docs/exai_feasibility_report.md`](docs/exai_feasibility_report.md) — Detailed research report on EXAI and `mithinsagar/exai-resumeintel-data`.
- [`docs/testing_report.md`](docs/testing_report.md) — Verification report across all 67 automated tests.
