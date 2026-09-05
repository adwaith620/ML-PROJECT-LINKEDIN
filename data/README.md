# Data Directory

This directory is used for local dataset storage. **Contents are gitignored** — do not commit data files to GitHub.

## Dataset Sources

All datasets used in this project are hosted on Hugging Face and loaded programmatically using the `datasets` library.

### 1. EXAI-ResumeIntel

**URL:** [https://huggingface.co/datasets/mithinsagar/exai-resumeintel-data](https://huggingface.co/datasets/mithinsagar/exai-resumeintel-data)

Two configurations:

| Configuration | Rows | Columns | Description |
|---------------|------|---------|-------------|
| `resumes` | 2,484 | 3 (`ID`, `Category`, `Feature`) | Processed resume text with 24 occupation categories |
| `job_postings` | ~1.62M | 2 (`Role`, `Features`) | Structured job posting text with role titles |

**Loading (resumes):**

```python
from datasets import load_dataset
ds = load_dataset("mithinsagar/exai-resumeintel-data", "resumes", split="train")
df = ds.to_pandas()
```

**Loading (job_postings — use streaming for large dataset):**

```python
from datasets import load_dataset
ds = load_dataset("mithinsagar/exai-resumeintel-data", "job_postings", split="train", streaming=True)
# Take a sample
sample = [record for i, record in enumerate(ds) if i < 5000]
```

### 2. Resume-Job Fit Merged v1

**URL:** [https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1](https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1)

| Split | Rows | Columns | Description |
|-------|------|---------|-------------|
| `train` | 80,017 | 6 | Resume-JD pairs with fit labels |
| `test` | 13,716 | 6 | Held-out test set |

Columns: `resume`, `jd`, `label`, `source`, `resume_domain`, `jd_domain`

Labels: `No Fit`, `Potential Fit`, `Good Fit`

**Loading:**

```python
from datasets import load_dataset
ds = load_dataset("med2425/resume-job-fit-merged-v1")
df_train = ds["train"].to_pandas()
df_test = ds["test"].to_pandas()
```

### 3. Resume NER Training Data

**URL:** [https://huggingface.co/datasets/yashpwr/resume-ner-training-data](https://huggingface.co/datasets/yashpwr/resume-ner-training-data)

| Split | Rows | Columns | Description |
|-------|------|---------|-------------|
| `train` | 22,855 | 1 (`messages`) | Chat-format NER-style annotations |

The `messages` column contains lists of `{content, role}` dictionaries in system/user/assistant chat format. This is not a traditional BIO-tagged NER dataset.

**Loading:**

```python
from datasets import load_dataset
ds = load_dataset("yashpwr/resume-ner-training-data", split="train")
df = ds.to_pandas()
```

## Important Notes

- These are **not** Kaggle datasets. They are hosted on Hugging Face.
- The EXAI-ResumeIntel `job_postings` configuration is very large (~1.62M records). Use **streaming** mode to avoid downloading the entire dataset.
- Raw datasets must **not** be committed to GitHub. They are excluded by `.gitignore`.
- Each team member should load datasets programmatically using the code above.

## Current Recommended Uses

| Dataset | Recommended Task |
|---------|-----------------|
| Resume-Job Fit Merged v1 | Primary dataset for supervised resume-JD matching (has fit labels) |
| EXAI-ResumeIntel (resumes) | Resume text source, category-level classification |
| EXAI-ResumeIntel (job_postings) | Job description corpus (streaming/sampling for experiments) |
| Resume NER Training Data | Resume information extraction (requires parsing chat format) |

See `docs/dataset_report.md` for the full dataset engineering analysis.
