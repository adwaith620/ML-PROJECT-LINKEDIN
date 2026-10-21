# Compatibility Scoring Methodology & Framework

**Project:** Resume Screening & Skill Gap Analysis System (TalentLens)  
**Version:** 1.1.0  
**Date:** October 2026  

---

## 1. Overview and Purpose

The TalentLens scoring system computes an objective, explainable **Compatibility Score** between a candidate's resume and a job description. The score is scaled to a continuous range of $[0.0, 100.0]$ and mapped to qualitative recommendation categories for recruiter decision support.

> **Important Disclaimer:** The compatibility score is an algorithmic decision-support estimate based on extracted textual evidence. It does not constitute a calibrated probability of hiring success, an evaluation of candidate character, or a guarantee of job performance. Automated decisions must not be made solely on this metric.

---

## 2. Mathematical Scoring Formula

The overall compatibility score $S_{\text{overall}}$ is calculated as a linear weighted combination of structured skill coverage, lexical baseline overlap, deep semantic alignment, and a bounded preferred qualification bonus:

$$S_{\text{overall}} = \min\left(100.0, \max\left(0.0, w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{baseline}} \cdot S_{\text{baseline}} + w_{\text{semantic}} \cdot S_{\text{semantic}} + B_{\text{preferred}}\right)\right)$$

Subject to:
$$\sum w_i = 1.0, \quad w_i \ge 0, \quad S_{\text{overall}} \in [0.0, 100.0]$$

---

## 3. Component Definitions and Normalization

### 3.1 Job Description Section Parsing & Requirement Separation
Job descriptions are parsed using section-aware segmentation into:
- **Required Qualifications ($\mathcal{K}_{\text{req}}$):** Hard requirements defining the denominator for coverage.
- **Preferred Qualifications ($\mathcal{K}_{\text{pref}}$):** Desirable or secondary competencies granting bonus points.
- **Contextual/Explanatory Skills:** Technologies mentioned only in general company overview or team descriptions (excluded from scoring).

When explicit headers are absent, an inference engine classifies sentences based on contextual modality cues ("must have", "required", "essential" vs. "nice to have", "plus", "preferred").

### 3.2 Multi-Tier Skill Match Classification & Partial Credit
Each required skill in $\mathcal{K}_{\text{req}}$ is classified into one of four states:
1. **Exact match:** Candidate explicitly demonstrates the requested canonical skill (credit $c = 1.0$).
2. **Recognized alias:** Candidate uses an accepted synonym or acronym (e.g., `k8s` for `Kubernetes`, `AWS` for `Amazon Web Services`, credit $c = 1.0$).
3. **Related or transferable skill:** Candidate demonstrates a documented related technology in the same domain with transferable credit $c_{\text{rel}} \in (0.0, 1.0)$:
   - Relational Databases (e.g., PostgreSQL for MySQL, MySQL for PostgreSQL): $c = 0.5$ (50%)
   - Cloud Providers (e.g., GCP or Azure for AWS): $c = 0.5$ (50%)
   - Containerization to Orchestration (e.g., Docker for Kubernetes): $c = 0.4$ (40%)
   - Frontend Frameworks (e.g., React for Vue.js): $c = 0.5$ (50%)
   - Python Backend Frameworks (e.g., Flask or Django for FastAPI): $c = 0.5$ (50%)
4. **Not evidenced:** No sufficient evidence found in the resume ($c = 0.0$).

### 3.3 Structured Skill Coverage ($S_{\text{skill}}$)
The skill match percentage is calculated strictly against the number of required skills $N_{\text{req}} = |\mathcal{K}_{\text{req}}|$:

$$U_{\text{matched}} = N_{\text{exact/alias}} + \sum_{j \in \text{Related}} c_j$$

$$S_{\text{skill}} = \begin{cases} 
\min\left(100.0, \left(\frac{U_{\text{matched}}}{N_{\text{req}}}\right) \times 100\right), & \text{if } N_{\text{req}} > 0 \\
100.0, & \text{if } N_{\text{req}} = 0 \text{ and candidate has evidenced skills} \\
0.0, & \text{if } N_{\text{req}} = 0 \text{ and candidate has no evidenced skills}
\end{cases}$$

### 3.4 Preferred Skill Bonus ($B_{\text{preferred}}$)
Preferred skills do not artificially inflate the required denominator. Instead, each evidenced preferred skill provides $+2.0$ bonus points, capped at $+5.0$ points:

$$B_{\text{preferred}} = \min(5.0, 2.0 \times N_{\text{pref\_matched}})$$

### 3.5 Lexical Baseline Similarity ($S_{\text{baseline}}$)
Measures keyword and n-gram overlap using TF-IDF feature representations:

$$S_{\text{baseline}} = \cos(\mathbf{v}_{\text{resume}}, \mathbf{v}_{\text{jd}}) \times 100 = \left( \frac{\mathbf{v}_{\text{resume}} \cdot \mathbf{v}_{\text{jd}}}{\|\mathbf{v}_{\text{resume}}\| \|\mathbf{v}_{\text{jd}}\|} \right) \times 100$$

### 3.6 Semantic Similarity ($S_{\text{semantic}}$)
Measures contextual alignment and domain proximity using Sentence-BERT (`all-MiniLM-L6-v2`):

$$S_{\text{semantic}} = \max\left(0.0, \cos(\mathbf{e}_{\text{resume}}, \mathbf{e}_{\text{jd}})\right) \times 100$$

For lengthy documents, text is partitioned into overlapping 200-word chunks (50-word overlap) and aggregated via mean-pooling.

---

## 4. Prioritized Evidence Extraction

Evidence snippets are selected using a strict priority hierarchy:
1. **Work Experience Sentences (Priority 1):** Real-world responsibility and achievement bullets.
2. **Project Descriptions (Priority 2):** Concrete project implementation context.
3. **Education & Certifications (Priority 3):** Formal academic background and credentials.
4. **Skills Inventory (Priority 4):** Comma-separated keyword lists (used only as fallback when no experiential context exists).

Duplicate snippet reuse is prevented: distinct skills select distinct sentences whenever multiple matching bullets exist.

---

## 5. Configurable Component Weights

The scoring weights are centrally managed in `src/scoring/config.py`:

| Mode | Skill Weight ($w_{\text{skill}}$) | Baseline TF-IDF ($w_{\text{baseline}}$) | Semantic S-BERT ($w_{\text{semantic}}$) | Description |
|---|---|---|---|---|
| **Hybrid (Default)** | **0.40 (40%)** | **0.20 (20%)** | **0.40 (40%)** | Multi-modal assessment combining explicit taxonomy, partial transfer credit, and semantic embeddings. |
| **Classical Fallback** | **0.60 (60%)** | **0.40 (40%)** | **0.00 (0%)** | Automatically engaged when Sentence-BERT is unavailable or offline. |

---

## 6. Recommendation Thresholds

| Score Interval | Category | Interpretation |
|---|---|---|
| **80.0% – 100.0%** | **Strong Match** | Candidate satisfies the vast majority of required competencies with strong domain alignment. |
| **60.0% – 79.9%** | **Moderate Match** | Candidate demonstrates core requirements with partial or transferable secondary competencies. |
| **40.0% – 59.9%** | **Potential Match** | Candidate possesses transferable foundational skills but notable gaps in core requirements. |
| **0.0% – 39.9%** | **Low Match** | Significant divergence in both required skill coverage and overall domain context. |

---

## 7. Known Limitations and Governance

1. **Unevidenced vs. Lacking:** The absence of a skill in a resume indicates that the term was not evidenced in the submitted text; it does not prove the candidate cannot perform the task.
2. **Transferable Credit Boundaries:** Transfer credit is bounded at $\le 0.5$ (or $\le 0.4$ for cross-layer skills like Docker $\to$ Kubernetes) and is explicitly tagged as "Related skill", never presented as an exact match.
3. **Scanned Documents:** The system extracts digital text. Image-only PDFs without OCR text layers return an explicit validation warning.
