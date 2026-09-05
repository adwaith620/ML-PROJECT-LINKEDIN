# Models Directory

This directory stores trained model artefacts. **Contents are gitignored** — do not commit model files.

## Directory Structure

```
models/
├── weights/          # Final trained model weights
├── checkpoints/      # Training checkpoints
└── README.md         # This file
```

## Model Artefacts

| Model | Format | Description |
|-------|--------|-------------|
| Sentence-BERT (fine-tuned) | `.pt` / `.bin` | Resume–JD semantic matching |
| Skill NER | `.pt` | Named entity recognition for skills |
| Scoring model | `.joblib` | Candidate ranking model |

## How to Obtain Models

Pre-trained and fine-tuned models will be hosted externally:
- **HuggingFace Hub:** *(add link when available)*
- **Google Drive:** *(add link when available)*

## Loading Models

```python
from sentence_transformers import SentenceTransformer

# Load fine-tuned model from local path
model = SentenceTransformer("models/weights/sbert-resume-matcher/")
```

> ⚠️ Never commit `.pt`, `.bin`, `.pkl`, `.joblib`, or `.ckpt` files to this repository.
