# System Architecture & Technical Specifications

**Project:** Resume Screening & Skill Gap Analysis System (TalentLens)  
**Architecture Pattern:** Client-Server Monorepo with Modular NLP/ML Processing Engine  
**Release Version:** 1.0.0  

---

## 1. High-Level Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             INTERVIEWER BROWSER                             │
│                  Vite + React 19 + TypeScript Application                   │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │ Resume Upload Panel   │  │ Job Description Panel│  │ Method Selector  │  │
│  │ (Drag & Drop / Pick)  │  │ (Paste / File Upload)│  │ (Hybrid/S-BERT)  │  │
│  └───────────┬───────────┘  └──────────┬───────────┘  └────────┬─────────┘  │
└──────────────┼─────────────────────────┼───────────────────────┼────────────┘
               │ Multipart Form Data     │                       │
               ▼                         ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI APPLICATION SERVER                         │
│                           (http://127.0.0.1:8000)                           │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │ /api/health (Status)  │  │ /api/analyze (POST)  │  │ /api/export/pdf  │  │
│  └───────────────────────┘  └──────────┬───────────┘  └────────▲─────────┘  │
└────────────────────────────────────────┼───────────────────────┼────────────┘
                                         │                       │
                                         ▼                       │
┌────────────────────────────────────────────────────────────────┼────────────┐
│                    TALENTLENS UNIFIED ML PIPELINE              │            │
│                         (src/pipeline.py)                      │            │
│                                                                │            │
│  1. Document Ingest & Limits Validation ◄──────────────────────┤            │
│     (src/resume_parser/parser.py & limits.py)                  │            │
│     - PDF (pypdf), DOCX (python-docx), TXT                     │            │
│     - Enforces 25MB resume, 10MB JD, 100 pages, 5MB text       │            │
│                                                                │            │
│  2. Text Normalization & Cleaning                              │            │
│     (src/preprocessing/text_cleaner.py)                        │            │
│     - Preserves C++, C#, .NET, Node.js, Python 3, CI/CD        │            │
│                                                                │            │
│  3. Skill & Entity Extraction                                  │            │
│     (src/skill_extraction/extractor.py & rule_based.py)        │            │
│     - Regex word boundary dictionary matching                  │            │
│     - Canonical alias resolution (k8s -> kubernetes)           │            │
│                                                                │            │
│  4. Genuine Text Evidence Extraction                           │            │
│     - Sentence-level extraction from candidate resume          │            │
│                                                                │            │
│  5. Multi-Modal Similarity Matching                            │            │
│     - Classical: TF-IDF Cosine Similarity (baseline.py)        │            │
│     - Semantic: Sentence-BERT all-MiniLM-L6-v2 (sentence_bert)│            │
│                                                                │            │
│  6. Skill Gap & Candidate Scoring                              │            │
│     (src/scoring/skill_gap.py & candidate_score.py)            │            │
│     - Matched skills, missing required skills, additional      │            │
│     - Weighted formula + recommendation tier                   │            │
│                                                                │            │
│  7. Professional Report Generation ────────────────────────────┘            │
│     (backend/pdf_generator.py via ReportLab)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure and Boundaries

```text
ML-PROJECT-LINKEDIN/
├── backend/                      # FastAPI application backend
│   ├── main.py                   # API routes, CORS, multipart ingest
│   └── pdf_generator.py          # ReportLab PDF report generation
│
├── frontend/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx               # Main workspace, dropzones, report viewer
│   │   ├── main.tsx              # React DOM entry point
│   │   ├── types.ts              # API TypeScript interfaces
│   │   └── styles.css            # Professional B2B CSS design system
│   ├── index.html                # HTML entry template
│   ├── package.json              # Frontend scripts and dependencies
│   ├── tsconfig.json             # TypeScript compiler settings
│   └── vite.config.ts            # Vite build and proxy config
│
├── src/                          # Core Machine Learning & NLP modules
│   ├── resume_parser/            # Document parsing (PDF, DOCX, TXT) & limits
│   ├── preprocessing/            # Text normalization, token preservation
│   ├── skill_extraction/         # Taxonomy dictionary, alias mapping, NER
│   ├── matching/                 # TF-IDF baseline & Sentence-BERT matcher
│   ├── scoring/                  # Skill gap analysis, weighted scoring
│   ├── evaluation/               # Metrics, explanation generator, leakage
│   └── pipeline.py               # Unified end-to-end orchestration pipeline
│
├── models/                       # Model artifacts and feature extractors
│   ├── baseline_feature_extractor.joblib  # Fitted TF-IDF vectorizer
│   └── baseline_model_lr.joblib           # Trained Logistic Regression model
│
├── tests/                        # 52 Automated unit and integration tests
├── docs/                         # Architecture, scoring, limits, EXAI audit
├── requirements.txt              # Backend and ML dependencies
└── run_local.bat                 # One-click Windows launch script
```

---

## 3. Data Flow & Security Considerations

1. **Transient Processing:** No candidate resumes or job descriptions are permanently written to persistent database records. All uploads are processed in temporary memory or bounded temporary disk buffers that are automatically discarded upon request completion.
2. **Defensive Parsing:**
   - PDF page count checked prior to text decompression.
   - Decompressed XML archives in DOCX files inspected for path traversal and compression bomb characteristics.
   - Strict size caps prevent memory exhaustion attacks.
3. **No External Cloud AI Dependencies:** All embeddings, TF-IDF vectors, and rule-based matches execute entirely on the local CPU or machine hardware without transmitting sensitive candidate resumes to external third-party LLM APIs.
