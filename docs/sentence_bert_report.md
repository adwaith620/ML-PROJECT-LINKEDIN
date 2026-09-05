# Semantic Matching Report (Phase 5)

## 1. Files Created/Modified
- `src/matching/sentence_bert.py`
- `tests/test_sentence_bert.py`
- `notebooks/05_sentence_bert_matching.ipynb`
- `docs/sentence_bert_report.md`

## 2. Sentence-BERT Model Selected
**Model:** `all-MiniLM-L6-v2` via `sentence-transformers`.

## 3. Reason for Selection
Semantic embeddings are necessary to capture the intent and contextual meaning of candidate skills rather than just lexical keyword overlaps (which Phase 4 evaluates). `all-MiniLM-L6-v2` was selected because:
- **Speed & Efficiency**: It runs blazingly fast, crucial for environments without robust GPUs (like standard Colab CPU instances).
- **Quality**: Despite its small size (~80MB), it retains high performance on Semantic Textual Similarity (STS) benchmarks.

## 4. Embedding Strategy
The `SemanticMatcher` class takes raw text (from Phase 2) and converts it into a 384-dimensional dense vector space where semantic proximity equates to geometric proximity.

## 5. Long-Document Strategy
Resumes typically exceed the 256-token limit of MiniLM. Truncation loses critical data. We employ a **sliding window chunking strategy**:
- The text is chunked into overlapping word windows (e.g., 200 words, 50-word overlap).
- Each chunk is embedded separately.
- **Aggregation**: A Mean Pooling operation averages the chunk embeddings into a single cohesive document-level vector, capturing the aggregate semantic intent without exceeding context limits.

## 6. Similarity Method
We utilize Scikit-Learn's **Cosine Similarity** (`cosine_similarity`). It normalizes vector magnitudes, effectively isolating the directional angle (semantic meaning) between the Resume vector and the Job Description vector, generating a continuous score between -1 and 1.

## 7. Threshold/Calibration Method
Fit classification mapping ("No Fit", "Potential Fit", "Good Fit") is handled via arbitrary default thresholds. *However*, the official thresholds must be empirically derived directly from the Validation distribution (carved exclusively out of the Train set) to avoid data leakage before evaluating the Test set.

## 8. Fine-Tuning Status
Fine-tuning with contrastive loss was intentionally skipped in this iteration. The goal is to establish the baseline efficacy of *Pretrained* Sentence-BERT against Phase 4's classical matching. Attempting to fine-tune on Colab without verified clean pairs can induce catastrophic forgetting.

## 9. Phase 4 Comparison Interface
The notebook produces a standardized JSON blob capturing identical evaluation metrics (`accuracy`, `macro_f1`, `weighted_f1`, `precision`, `recall`). Phase 4 results can simply be appended to a master table comparing this JSON to objectively determine if semantic matching outperformed TF-IDF.

## 10. Error Analysis
- **False Positives**: Keyword-heavy, generic resumes map tightly to generic job descriptions despite lacking true technical depth.
- **False Negatives**: Highly specific domain acronyms that the pretrained model hasn't seen during pretraining (e.g., proprietary internal tools) cause drops in similarity even if they are exact keyword matches.

## 11. Limitations
The primary limitation is the mean-pooling approach over long documents; very specific signals (like a crucial required skill) can be diluted by the "average" meaning of the rest of a verbose resume.

## 12. Google Colab Status
The notebook is fully compatible with Google Colab and installs necessary libraries inline.

## 13. Commit Hash
*Not applicable due to environment constraints.*

## 14. Push Status
*Not applicable due to environment constraints.*
