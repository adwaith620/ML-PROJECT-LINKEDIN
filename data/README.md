# Data Directory

This directory holds all datasets used in the project. **Contents are gitignored** — do not commit data files.

## How to Obtain Datasets

### 1. Resume Dataset
- **Source:** [Kaggle — Resume Dataset](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset)
- **Download:** Use Kaggle CLI or download manually
  ```bash
  kaggle datasets download -d gauravduttakiit/resume-dataset -p data/raw/
  ```
- **Place in:** `data/raw/resumes/`

### 2. Job Descriptions Dataset
- Collected from Kaggle / custom scraping
- **Place in:** `data/raw/job_descriptions/`

### 3. Skills Taxonomy
- [ESCO Classification](https://esco.ec.europa.eu/)
- [O*NET Online](https://www.onetonline.org/)
- **Place in:** `data/raw/skills/`

## Directory Structure

```
data/
├── raw/              # Original, unmodified datasets
│   ├── resumes/
│   ├── job_descriptions/
│   └── skills/
├── processed/        # Cleaned and transformed data
│   ├── resumes/
│   └── job_descriptions/
└── README.md         # This file
```

## Shared Storage

If datasets are hosted on a shared drive, link them here:
- **Google Drive:** *(add link when available)*
- **HuggingFace:** *(add link when available)*

> ⚠️ Never commit CSV, Parquet, or other large data files to this repository.
