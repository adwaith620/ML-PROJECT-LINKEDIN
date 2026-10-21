# Phase 6: Candidate Scoring and Skill Gap Analysis

## 1. Objective
Phase 6 bridges the gap between raw data processing, baseline ML text matching, and information extraction. It aggregates these signals into an explainable, structured recommendation for candidate-job matching.

## 2. Inputs
The scoring system takes the following conceptual inputs:
- Candidate Skills (Array of strings, expected from Phase 3)
- Required Job Skills (Array of strings)
- Optional Job Skills (Array of strings)
- Baseline Match Score (Float [0,1], from Phase 4)
- *Future:* Semantic Similarity Score (Float [0,1], from Phase 5)

## 3. Skill Normalization
To prevent false negatives in skill matching (e.g., rejecting "ML" when "Machine Learning" is required), skills pass through a normalization layer.
- `src.scoring.skill_gap.normalize_skill` lowercases, strips whitespace, and maps common abbreviations (e.g., `js` -> `javascript`) via a controlled, hardcoded dictionary (`SKILL_NORMALIZATION_MAP`).
- This allows explicit control over equivalencies rather than relying on unpredictable fuzzy string matching.

## 4. Skill-Gap Methodology
The system uses set operations to categorize skills:
- **Matched Required:** Intersection of normalized candidate skills and required skills.
- **Matched Optional:** Intersection of candidate skills and optional skills.
- **Missing Required:** Required skills minus candidate skills.
- **Missing Optional:** Optional skills minus candidate skills.
- **Additional Skills:** Candidate skills that are neither required nor optional.

The *Skill Match Percentage* is calculated strictly against *required* skills.

## 5. Scoring Methodology
The overall candidate score is a weighted aggregate of three potential sub-scores, scaled from `[0, 100]`:
1. **Skill Score:** (Matched Required / Total Required) * 100
2. **Text Baseline Score:** Output of Phase 4 (e.g., Logistic Regression probability or scaled TF-IDF similarity).
3. **Semantic Text Score:** Output of Phase 5 (Sentence-BERT similarity).

## 6. Weight Configuration
Weights are entirely configurable via `src/scoring/config.py`:
- **Without Phase 5:** Skills (60%), Baseline Text (40%).
- **With Phase 5:** Skills (40%), Baseline Text (20%), Semantic Text (40%).
*Reasoning:* Structured skills are a hard requirement for HR filtering. The baseline text provides a keyword backup. When Phase 5 is active, the semantic understanding replaces the majority of the keyword reliance.

## 7. Ranking Methodology
The `rank_candidates` function takes a list of candidate dictionaries and a job requirement dictionary. It performs gap analysis, computes the overall score, and returns the list of candidates sorted by `overall_score` descending. 

## 8. Recommendation Categories
Scores are discretized into interpretative buckets:
- `>= 80.0`: **Strong Match**
- `>= 60.0`: **Moderate Match**
- `>= 40.0`: **Potential Match**
- `< 40.0`: **Low Match**

These categories explicitly separate the numerical score from the hiring claim, preventing the system from making absolute "hire" assertions.

## 9. Explainability
The output for each candidate is heavily structured to explain *why* a score was given:
```json
{
  "overall_score": 85.0,
  "recommendation": "Strong Match",
  "skill_match_percentage": 100.0,
  "missing_required_skills": [],
  "score_breakdown": {
    "skill_contribution": 60.0,
    "baseline_text_contribution": 25.0
  }
}
```
This ensures a frontend dashboard can surface missing requirements immediately to recruiters.

## 10. Limitations
- Basic exact/dictionary matching for skills limits flexibility if an alias is missing from `SKILL_NORMALIZATION_MAP`.
- Treating all required skills with equal weight ignores cases where one skill is an absolute dealbreaker while another is merely preferred.

## 11. Phase 5 Integration Plan
The system is explicitly built to be decoupled from Phase 5 (Sentence-BERT).
- `calculate_candidate_score` accepts an optional `semantic_score` argument.
- By default, it is `None`, and the system uses the 60/40 skill/baseline weight split.
- Once Phase 5 is completed, passing the Sentence-BERT score into this function automatically shifts the internal weights (to 40/20/40) without requiring any changes to the Phase 6 module.

## 12. Future Improvements
- Implement TF-IDF or embedding-based soft matching for skill variations rather than relying entirely on a hardcoded map.
- Allow variable weighting per required skill (e.g., "Must Have" vs "Nice to Have").
