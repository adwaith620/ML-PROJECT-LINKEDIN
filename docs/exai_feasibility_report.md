# Explainable AI (EXAI) Feasibility Report

**Project:** Resume Screening & Skill Gap Analysis System  
**Date of Research:** October 21, 2026  
**Author:** AI Technical Research & ML Engineering Pair  
**Subject Resource:** `mithinsagar/exai-resumeintel-data` ([Hugging Face Hub Dataset](https://huggingface.co/datasets/mithinsagar/exai-resumeintel-data))

---

## Executive Summary

Explainable AI (EXAI) was evaluated as a potential extension for the candidate screening and skill-gap analysis pipeline. This research investigated whether integrating an external EXAI resource—specifically the `mithinsagar/exai-resumeintel-data` dataset on Hugging Face—is technically feasible, methodologically sound, and practically justified for this academic project.

**Primary Finding:**  
The dataset `mithinsagar/exai-resumeintel-data` **contains zero explainability annotations, rationale ground truth, feature attributions, or paired compatibility judgments**. The word "exai" exists solely in the dataset namespace/identifier. Attempting to use this dataset to train or fine-tune an explainability system would require extensive manual annotation and would risk generating unfaithful, hallucinated natural language rationales rather than true mechanistic explanations.

**Final Recommendation:**  
**Do NOT implement a generative EXAI model.** Instead, retain and present the project's **transparent, non-generative, evidence-backed breakdown system** (which provides exact matched skills with authentic resume sentence snippets, missing required skills, and explicit mathematical component contributions). This transparent approach is 100% faithful to the underlying algorithms, zero-latency, zero-hallucination, and fully aligned with recruitment compliance principles.

---

## 1. What EXAI Means for This Specific Project

In the context of the Resume Screening & Skill Gap Analysis System, explainability addresses a critical recruitment challenge: **Why did candidate X receive a score of Y% for job posting Z?**

For recruiters and hiring managers, an explanation must answer:
1. Which specific required skills were satisfied, and where in the resume was the evidence found?
2. Which mandatory or preferred competencies were missing or unevidenced?
3. How much did lexical keyword matching vs. deep semantic embedding contribute to the composite score?
4. What qualitative factors (e.g., years of experience, degree level) influenced the final categorization?

True EXAI in this domain requires **faithfulness** (the explanation must reflect the actual computations of the model) and **interpretability** (the output must be intelligible to human interviewers without data science expertise).

---

## 2. In-Depth Investigation of `mithinsagar/exai-resumeintel-data`

*Accessed and programmatically inspected on October 21, 2026 using the Hugging Face `datasets` library.*

### 2.1 Dataset Configurations and Schemas

The dataset exposes two configurations:

| Configuration | Split | Rows | Schema / Columns | Content Description |
|---|---|---|---|---|
| `resumes` | `train` | 2,484 | `ID: int64`<br>`Category: string`<br>`Feature: string` | Text of resumes categorized into 24 broad industry occupations (e.g., HR, Engineering, Sales). `Feature` contains lowercase, space-separated resume text. |
| `job_postings` | `train` | ~1.62M | `Role: string`<br>`Features: string` | Job posting records with role titles and concatenated requirement text. |

### 2.2 Lack of Explainability Ground Truth

Our programmatic inspection confirmed:
1. **No Rationale Data:** There are no human-written explanations, acceptance/rejection justifications, or hiring decisions.
2. **No Pairwise Linkage:** The resumes and job postings are independent, unlinked corpora. There are no candidate-job pairs with associated ground-truth compatibility labels or counterfactual comparisons.
3. **No Token Attribution:** Neither configuration contains saliency masks, entity span tags, or attention target annotations.

**Conclusion on Resource:** `mithinsagar/exai-resumeintel-data` is an unaligned corpus of resume texts and job descriptions, not an Explainable AI benchmark. The prefix "exai" in the repository name appears to be the author's research project moniker rather than a description of the dataset contents.

---

## 3. Compatibility with Existing Pipeline

The current system calculates candidate-job fit using:
1. Rule-based skill extraction with alias normalisation (`src/skill_extraction`).
2. Classical TF-IDF lexical cosine similarity via pre-trained `BaselineFeatureExtractor` (`src/matching/baseline.py`).
3. Dense semantic embeddings via Sentence-BERT `all-MiniLM-L6-v2` (`src/matching/sentence_bert.py`).
4. Structured skill gap analysis (`src/scoring/skill_gap.py`).
5. Configurable weighted scoring formula (`src/scoring/candidate_score.py`).

The `mithinsagar/exai-resumeintel-data` dataset cannot be plugged into this pipeline. It provides no training signals that align with our feature extractor or our Sentence-BERT semantic matcher.

---

## 4. Resource & Engineering Requirements for Model-Based EXAI

If the team were to pursue generative or surrogate EXAI (e.g., training a Seq2Seq model or prompting an LLM to generate post-hoc rationales, or applying SHAP / LIME):

1. **Annotation Overhead:** Constructing an aligned dataset of at least 2,000–5,000 resume-JD pairs with certified human explanations would take hundreds of hours of professional recruiting annotation.
2. **Compute Requirements:** Fine-tuning an open-source model (e.g., Llama-3-8B or Mistral-7B) for rationale generation would require dedicated GPU clusters (A100 / RTX 4090), exceeding standard student hardware budgets.
3. **Inference Latency:** Running local LLM inference per uploaded document would increase screening latency from ~1.5 seconds to 15–45 seconds per resume.
4. **Surrogate Instability:** Classical perturbations (e.g., LIME or KernelSHAP on dense Sentence-BERT vectors) require generating thousands of text perturbations per document, leading to high variance and long execution times on multi-page resumes.

---

## 5. Faithfulness vs. Plausibility (The Post-Hoc Fallacy)

A fundamental risk in modern Explainable AI is confusing **plausibility** with **faithfulness**:
- **Plausible Explanation:** Text that sounds convincing and polite to a human recruiter (e.g., *"The candidate demonstrated leadership in cloud environments"*), generated by an autoregressive language model.
- **Faithful Explanation:** An explanation that strictly reflects the internal mathematical mechanisms that produced the score.

If a generative model produces an explanation for a score computed by Sentence-BERT + TF-IDF, it has no direct visibility into why two 384-dimensional dense vectors had a cosine similarity of 0.82. The generative model will invent plausible-sounding justifications that may have had zero impact on the actual vector dot product. This represents **post-hoc rationalisation**, which is misleading and unacceptable in hiring technology.

---

## 6. Risks: Hallucination, Bias, Privacy, and Legal Considerations

1. **Hallucination of Qualifications:** Generative EXAI models frequently hallucinate certifications, degrees, or skills that do not exist in the candidate's actual text.
2. **Algorithmic Bias Amplification:** Generating natural language rationales from uncurated web datasets risks perpetuating gender, racial, and regional linguistic biases.
3. **Legal & Compliance Scrutiny:** Employment screening algorithms are governed by regulations (e.g., EEOC Uniform Guidelines in the US, EU AI Act for High-Risk AI Systems, and local employment laws). Systems that provide false or unfaithful explanations for hiring recommendations expose institutions to regulatory liability.
4. **Data Leakage & Privacy:** Feeding candidate resumes to third-party generative APIs to obtain "explanations" violates candidate data confidentiality and GDPR/privacy constraints.

---

## 7. Feasibility Assessment for a Five-Member BTech Team

| Criterion | Evaluation | Assessment |
|---|---|---|
| Technical Difficulty | Very High | Requires building synthetic pairwise corpora, fine-tuning LLMs, or debugging high-dimensional attribution spaces. |
| Time Constraint | Prohibitive | Exceeds the remaining semester timeframe without compromising core full-stack and ML deliverables. |
| Hardware Demands | Impractical | Requires dedicated GPU hardware for training and low-latency inference. |
| Maintenance Overhead | High | Generative explanations require constant guardrails and hallucination checks. |

**Overall Team Feasibility:** **Not Feasible** for the scope of a standard undergraduate engineering capstone.

---

## 8. The Recommended Solution: Transparent Non-Generative Explainability

Rather than introducing an opaque generative model to explain another model, the system implements **intrinsic, deterministic transparency**:

1. **Skill Gap Auditing:**
   - Every matched skill is displayed with an authentic, unedited sentence snippet extracted directly from the candidate's resume (`matched_skills`).
   - Every missing competency is explicitly tagged as "Not found in resume" rather than assuming candidate incompetence.
2. **Mathematical Score Decomposition:**
   - The final score is openly decomposed into its constituent inputs:
     $$\text{Score} = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{baseline}} \cdot S_{\text{baseline}} + w_{\text{semantic}} \cdot S_{\text{semantic}}$$
   - Recruiters can inspect the exact weights used (e.g., 40% skills, 20% TF-IDF, 40% Sentence-BERT).
3. **Zero Hallucination:**
   - Every word presented as evidence was written by the candidate.
4. **Instantaneous Execution:**
   - Adds zero compute overhead to the screening workflow.

This transparent framework is already fully implemented in `src/pipeline.py`, rendered in the web UI, and documented in `src/evaluation/explainability.py`.

---

## 9. Definite Recommendation

1. **Do not integrate `mithinsagar/exai-resumeintel-data` into the project runtime.**
2. **Do not implement a generative or surrogate EXAI model in the current release.**
3. **Deploy the implemented deterministic, evidence-backed transparency subsystem as the project's explainability component.**
4. **In the capstone presentation, present this choice as a deliberate, principled engineering decision prioritizing auditability, compliance, and hallucination prevention over black-box generative text.**

---

## 10. Conditions That Would Warrant Future Re-evaluation

A future team could re-evaluate this recommendation only if:
1. A peer-reviewed, human-validated benchmark of paired resume-JD explanations with token-level attribution (e.g., a standardized CoT hiring benchmark) is publicly released.
2. Compute infrastructure with low-latency local inference (e.g., on-device 4-bit quantized SLMs) is guaranteed in the deployment environment.
3. Formal human evaluation protocols (measuring recruiter task completion and attribution faithfulness) are established prior to training.
