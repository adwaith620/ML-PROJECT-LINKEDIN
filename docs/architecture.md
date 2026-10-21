# System Architecture & Technical Specifications

**Project:** Resume Screening & Skill Gap Analysis System (TalentLens)  
**Architecture Pattern:** Client-Server Monorepo with Modular NLP/ML Processing Engine  
**Release Version:** 1.1.0  

---

## 1. High-Level Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             INTERVIEWER BROWSER                             │
│       Vite + React 19 + TypeScript + WCAG 2.2 AA Accessible Dark Mode       │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │ Resume Upload Panel   │  │ Job Description Panel│  │ Theme Controller │  │
│  │ (Drag & Drop / Pick)  │  │ (Paste / File Upload)│  │ (Light / Dark)   │  │
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
│  3. JD Section Parsing (Required vs. Preferred)                │            │
│     (src/skill_extraction/jd_parser.py)                        │            │
│     - Distinguishes Required, Preferred, and Contextual skills │            │
│                                                                │            │
│  4. Centralized Taxonomy & Aliases                             │            │
│     (src/skill_extraction/skill_dictionary.py)                 │            │
│     - Canonical master taxonomy (200+ tech skills & aliases)   │            │
│     - Transferable domain relations (PostgreSQL <-> MySQL)     │            │
│                                                                │            │
│  5. Multi-Tier Match Classification & Prioritized Evidence     │            │
│     (src/skill_extraction/match_classifier.py)                 │            │
│     - Exact match, Recognized alias, Related skill (transfer)  │            │
│     - Prioritizes Work Experience -> Projects -> Education     │            │
│                                                                │            │
│  6. Multi-Modal Similarity Matching                            │            │
│     - Classical: TF-IDF Cosine Similarity (baseline.py)        │            │
│     - Semantic: Sentence-BERT all-MiniLM-L6-v2 (sentence_bert)│            │
│                                                                │            │
│  7. Skill Gap & Candidate Scoring                              │            │
│     (src/scoring/candidate_score.py)                           │            │
│     - Transparent breakdown, explicit denominator, bonus       │            │
│                                                                │            │
│  8. Formatted PDF Report Generator                             │            │
│     (backend/pdf_generator.py)                                 │            │
│     - Professional vector PDF matching online dashboard        │            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory and Module Organization

```text
ML-PROJECT/
├── backend/                  # FastAPI web server and PDF export
│   ├── main.py               # REST API endpoints & CORS configuration
│   └── pdf_generator.py      # Multi-tier ReportLab PDF generator
├── frontend/                 # React 19 + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx           # Main workspace, results dashboard, dark theme
│   │   ├── styles.css        # WCAG 2.2 AA compliant CSS design tokens
│   │   └── types.ts          # Complete TypeScript interfaces
│   └── package.json
├── src/                      # Core Machine Learning & NLP pipeline
│   ├── preprocessing/        # Document text cleaning & token preservation
│   ├── resume_parser/        # Multi-format ingestion (PDF, DOCX, TXT)
│   ├── skill_extraction/     # Taxonomy, JD parser, classifier & evidence
│   │   ├── skill_dictionary.py   # Centralized canonical taxonomy & aliases
│   │   ├── jd_parser.py          # Section-aware JD segmentation
│   │   ├── match_classifier.py   # Multi-tier classification & evidence
│   │   ├── rule_based.py         # Boundary-safe regex extraction
│   │   └── normalization.py      # Canonical normalization
│   ├── matching/             # TF-IDF & Sentence-BERT embedding matchers
│   ├── scoring/              # Weighted score aggregation & config
│   └── pipeline.py           # Unified end-to-end execution pipeline
├── tests/                    # 67 unit & integration tests (100% pass)
└── docs/                     # Comprehensive engineering documentation
```

---

## 3. UI/UX & Dark Mode Design System

- **Design Philosophy:** Clean, institutional engineering console avoiding neon accents or harsh pitch-black backgrounds.
- **Accessibility:** Fully compliant with WCAG 2.2 AA contrast standards ($\ge 4.5:1$ for normal body text, $\ge 3:1$ for headers and UI component boundaries).
- **Design Tokens:**
  - Light mode: Surface `#ffffff`, Background `#f8fafc`, Primary text `#0f172a`.
  - Dark mode: Surface `#1e293b` (slate 800), Background `#0b0f19` (rich slate navy), Primary text `#f8fafc`.
  - Match pills: Exact (`emerald`), Related (`purple/indigo`), Missing (`amber`), Preferred (`sky/cyan`).
- **Persistence:** User theme preferences persist via `localStorage` with system `prefers-color-scheme` fallback.
