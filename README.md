# Intelligent Explainable Resume Screening & Skill Gap Analysis System

> **Using NLP and Sentence-BERT** — BTech CS/AI Academic Project (5 Members)

---

## 🎯 Project Objective

Build an **intelligent, explainable resume screening system** that:

1. **Parses resumes** (PDF/DOCX) and extracts structured information (skills, experience, education).
2. **Matches candidates to job descriptions** using semantic similarity powered by **Sentence-BERT** embeddings.
3. **Scores and ranks** candidates with transparent, weighted criteria.
4. **Explains every decision** — recruiters see *why* a candidate was ranked higher or lower (LIME / SHAP / attention-based explanations).
5. **Identifies skill gaps** — highlights missing skills and suggests upskilling paths for candidates.

The goal is to move beyond keyword-matching approaches and provide **fair, interpretable, and semantically-aware** resume screening.

---

## 🏗️ High-Level Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Resume     │────▶│  Resume Parser   │────▶│ Skill Extraction │
│  (PDF/DOCX) │     │  (text + struct)  │     │  (NER / rules)   │
└─────────────┘     └──────────────────┘     └────────┬─────────┘
                                                       │
┌─────────────┐     ┌──────────────────┐               │
│  Job Desc.  │────▶│  JD Parser       │───────────────┤
│  (text)     │     │  (requirements)   │               │
└─────────────┘     └──────────────────┘               ▼
                                              ┌──────────────────┐
                                              │  Semantic Matcher │
                                              │  (Sentence-BERT)  │
                                              └────────┬─────────┘
                                                       │
                                    ┌──────────────────┼──────────────────┐
                                    ▼                  ▼                  ▼
                           ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
                           │  Scoring &   │  │  Skill Gap   │  │  Explainability  │
                           │  Ranking     │  │  Analysis    │  │  (LIME / SHAP)   │
                           └──────────────┘  └──────────────┘  └──────────────────┘
                                    │
                                    ▼
                           ┌──────────────────────────────┐
                           │  Web Dashboard (Streamlit)    │
                           │  Recruiters & Candidates      │
                           └──────────────────────────────┘
```

---

## 📊 Dataset Sources

| Dataset | Description | Source |
|---------|-------------|--------|
| Resume Dataset (Kaggle) | ~2,400 labelled resumes across 25+ categories | [Kaggle](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset) |
| Job Descriptions Dataset | Structured JD corpus with required skills | [Kaggle](https://www.kaggle.com/datasets) / Custom collected |
| LinkedIn Skills Taxonomy | Standardised skill ontology | [LinkedIn / ESCO](https://esco.ec.europa.eu/) |
| O*NET Skills Database | Occupation-specific skill requirements | [O*NET Online](https://www.onetonline.org/) |

> **⚠️ Note:** Raw datasets and model weights are **NOT** stored in this repository. See [Data & Model Storage Strategy](#-data--model-storage-strategy) below.

---

## 📁 Repository Structure

```
ML-PROJECT-LINKEDIN/
│
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .gitignore                # Excludes data, models, caches
│
├── data/                     # Data directory (contents gitignored)
│   └── README.md             # Instructions for obtaining datasets
│
├── notebooks/                # Jupyter notebooks for EDA & experiments
│
├── src/                      # Core source code
│   ├── preprocessing/        # Text cleaning, normalisation
│   ├── resume_parser/        # PDF/DOCX parsing, structure extraction
│   ├── skill_extraction/     # NER-based and rule-based skill extraction
│   ├── matching/             # Sentence-BERT semantic matching
│   ├── scoring/              # Candidate scoring & ranking logic
│   ├── explainability/       # LIME, SHAP, attention explanations
│   └── evaluation/           # Metrics, benchmarks, evaluation scripts
│
├── models/                   # Saved models (contents gitignored)
│   └── README.md             # Instructions for model artefacts
│
├── backend/                  # API server (FastAPI / Flask)
├── frontend/                 # Web UI (Streamlit / React)
├── tests/                    # Unit and integration tests
└── docs/                     # Documentation, reports, diagrams
```

---

## 🔄 Development Phases

### Phase 1 — Project Setup & Data Collection *(Current)*
- Repository structure, dependencies, team onboarding
- Identify and download datasets
- Initial EDA in notebooks

### Phase 2 — Data Preprocessing & Feature Engineering
- Resume parsing pipeline (PDF → structured text)
- Text cleaning, normalisation, tokenisation
- Skill taxonomy mapping

### Phase 3 — Model Development
- Sentence-BERT fine-tuning for resume–JD matching
- Skill extraction (NER + rule-based hybrid)
- Scoring algorithm design

### Phase 4 — Explainability & Skill Gap Analysis
- LIME / SHAP integration for match explanations
- Skill gap identification and visualisation
- Bias detection and fairness auditing

### Phase 5 — Integration & Deployment
- Backend API development
- Frontend dashboard
- End-to-end testing and evaluation
- Final documentation and presentation

---

## 👥 Team Responsibilities

| Member | Role | Primary Modules |
|--------|------|-----------------|
| Member 1 | Project Lead / NLP Engineer | `src/preprocessing/`, `src/resume_parser/` |
| Member 2 | ML Engineer | `src/matching/`, `src/scoring/` |
| Member 3 | NLP / Skill Extraction | `src/skill_extraction/`, data collection |
| Member 4 | Explainability & Evaluation | `src/explainability/`, `src/evaluation/` |
| Member 5 | Full-Stack / Integration | `backend/`, `frontend/`, `tests/` |

> Update this table with actual team member names once finalised.

---

## 💾 Data & Model Storage Strategy

This repository follows a **code-only** policy for version control:

| What | Where | Tracked in Git? |
|------|-------|-----------------|
| Source code | `src/`, `backend/`, `frontend/` | ✅ Yes |
| Notebooks | `notebooks/` | ✅ Yes |
| Documentation | `docs/`, `README.md` | ✅ Yes |
| Raw datasets | `data/raw/` | ❌ No (gitignored) |
| Processed data | `data/processed/` | ❌ No (gitignored) |
| Model weights | `models/weights/` | ❌ No (gitignored) |
| Checkpoints | `models/checkpoints/` | ❌ No (gitignored) |

**For large files**, use one of:
- **Google Drive** shared folder (link in `data/README.md`)
- **HuggingFace Hub** for model artefacts
- **DVC (Data Version Control)** if the team adopts it later

Each team member should download datasets locally using instructions in `data/README.md`.

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/250529-dotcom/ML-PROJECT-LINKEDIN.git
cd ML-PROJECT-LINKEDIN

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 📄 License

The project has been developed as an academic exercise as part of the CS(AI) curriculum for the academic year 2026-27.

---

*Last updated: September 2026*
