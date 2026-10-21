# Phase 7: Model Evaluation & Explainability

## 1. Evaluation Objective
The objective of Phase 7 is to formally evaluate the Phase 4 Baseline (Logistic Regression on TF-IDF) and Phase 5 (Sentence-BERT), compare their performances, and validate the Phase 6 Explainability generation logic. This guarantees our final scores are statistically backed and interpretable.

## 2. Dataset and Split Strategy
We use the primary dataset: `med2425/resume-job-fit-merged-v1`. 
The official `test` split (approx. 13.7k records) was explicitly held out during all feature engineering and model training steps in Phases 4 and 5. This strict split ensures evaluating the true generalization capability of the text matching models.

## 3. Evaluation Metrics
For candidate matching, the following metrics were prioritized:
- **Macro F1 Score:** Averages the F1 across "Good Fit", "Potential Fit", and "No Fit", heavily penalizing models that only predict the majority class (No Fit).
- **Class-Specific F1 / Precision / Recall:** Provides visibility into how the model handles edge cases and minority categories.
- **Accuracy:** General hit-rate context, though unreliable on its own due to heavy label imbalance.

## 4. Phase 4 Results (Baseline)
The Phase 4 Logistic Regression model achieved strong baseline performance due to the lexical overlap between synthetic resumes and JDs. However, its primary weakness is semantic ignorance: a resume mentioning "React" and a JD requesting "Frontend Engineer" yield minimal similarity.

## 5. Phase 5 Results (Sentence-BERT)
Phase 5 utilizes `all-MiniLM-L6-v2`, resolving vocabulary mismatches by mapping resumes and JDs to a shared 384-dimensional dense semantic space. 
*(Note: Refer to the Notebook for real-time comparative outputs).*

## 6. Baseline vs Sentence-BERT Comparison
Sentence-BERT typically yields higher macro recall, as it identifies "Potential Fits" based on structural similarities rather than just exact keyword hits. The comparison highlights that TF-IDF acts as a strict keyword filter, whereas Sentence-BERT acts as a conceptual linker.

## 7. Phase 6 Scoring Evaluation
The final candidate scoring aggregates three signals:
- Structured Skills
- Baseline Text
- Semantic Text
The `generate_candidate_explanation` function was verified to accurately reflect the configurable weights (`src/scoring/config.py`) and cap the maximum score at 100.0 properly.

## 8. Error Analysis
Common failure modes discovered during False Positive / False Negative analysis:
- **Seniority Mismatches:** Both Phase 4 and Phase 5 models struggle to distinguish a "Junior Data Scientist" resume from a "Lead Data Scientist" JD, because the dense keyword structures are heavily overlapping.
- **Synthetic Data Artifacts:** Some "No Fit" labels from the dataset generator appear overly harsh when evaluated by a human, leading to perceived model "errors" that are actually dataset errors.

## 9. Explainability Methodology
Candidates receive a comprehensive breakdown to prevent the AI from acting as a "black box":
1. **Top-line Score and Recommendation category** (e.g., 85/100, Strong Match)
2. **Component Breakdown** (showing exact point contributions of Skills vs Text)
3. **Structured Skill Gaps** (Matched vs Missing Required Skills)
4. **Natural Language Summary** explaining the primary driver of the score.

## 10. Score Contribution Analysis
Using the standard configuration:
- Skills contribute up to 40 points.
- Sentence-BERT contributes up to 40 points.
- Baseline TF-IDF contributes up to 20 points.
This balanced approach prevents a resume completely devoid of required skills from scoring highly based solely on stylistic resemblance.

## 11. Leakage Analysis
The `check_data_leakage` function was run across the Train and Test splits. By casting text to lowercase, stripping whitespace, and checking exact intersections, we verify that the dataset creator did not mistakenly leak Test resumes into the Train split.

## 12. Bias/Limitations
- **Demographic Bias:** The source dataset does not contain metadata regarding gender, ethnicity, or age. Therefore, we cannot perform standard demographic parity checks. 
- **Language Limitations:** Both TF-IDF stopwords and the Sentence-BERT vocabulary are English-optimized.
- **Label Bias:** The dataset uses synthetically generated labels (`source='generated_smart'`). We are effectively training the model to mimic the heuristic generator.

## 13. Key Findings
- Extracting hard skills (Phase 3) is critical; text similarity models (Phase 4/5) alone are insufficient for technical hiring because they miss discrete capability checks (like missing Docker).
- The hybrid scoring mechanism successfully bridges determinism (skills) with fuzzy logic (Sentence-BERT).

## 14. Future Improvements
- Expand the `SKILL_NORMALIZATION_MAP` into a proper taxonomic graph.
- Implement soft-margin thresholds where "Junior" vs "Senior" automatically deducts points regardless of semantic overlap.
