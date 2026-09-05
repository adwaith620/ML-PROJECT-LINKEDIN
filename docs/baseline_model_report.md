# Phase 4: Baseline Resume-Job Matching Model

## 1. Objective
The objective of Phase 4 is to establish a strong, reproducible classical machine-learning baseline for predicting the semantic fit between a candidate's resume and a job description. This provides a performance floor that the advanced semantic matching models (Phase 5) must demonstrably beat.

## 2. Dataset
- **Primary Source:** `Resume-Job Fit Merged v1`
- **Text Processing:** The input strings are normalized and cleaned using the Phase 2 pipeline (`src.preprocessing.text_cleaner`), which specifically preserves critical technical tokens (e.g., `C++`, `Node.js`).

## 3. Split Strategy
To avoid test set leakage, the official test split (13,716 records) provided in the dataset is strictly held out. The training partition is subsampled and further split into an internal 80/20 Train/Validation set. All splits are stratified by the `label` column to handle the severe class imbalance natively present in the data.

## 4. Feature Engineering
The features engineered for the classical baseline include:
- **TF-IDF Cosine Similarity:** The TF-IDF vocabulary (capped at 5,000 features, ignoring English stop words) is fitted exclusively on the training text. Both the resumes and JDs are transformed, and the cosine similarity between the vectors is calculated.
- **Length Metrics:** `resume_char_len`, `jd_char_len`
- **Word Counts:** `resume_word_count`, `jd_word_count`
- **Ratio Features:** `length_ratio` (resume length / JD length)

*Leakage Prevention:* Target labels were NOT used to derive any of the features. The TF-IDF matrix was strictly fitted on the `train` slice before any transformation occurred on `validation` or `test`.

## 5. Models Evaluated
The following models were trained and compared:
1. **Logistic Regression** (L2 penalty)
2. **Linear SVM** (LinearSVC)
3. **Random Forest Classifier**

## 6. Class Imbalance Handling
The dataset exhibits a roughly 10:1 imbalance between "No Fit" and "Good Fit".
- Stratification guarantees that the 7.24% minority class is adequately represented across train, validation, and test sets.
- `class_weight='balanced'` was applied to all models. This penalizes the model heavily for misclassifying minority classes (Good Fit/Potential Fit) compared to the majority class.

## 7. Evaluation Metrics
Models were evaluated using:
- **Macro F1 Score:** The primary metric, as it averages F1 across all three classes equally regardless of support size, heavily penalizing models that ignore the minority class.
- **Precision / Recall / F1-Score per class**
- **Accuracy**
- **Confusion Matrix**

## 8. Results
(Exact metrics are logged in `notebooks/04_baseline_matching.ipynb`). 
Linear models (Logistic Regression, Linear SVM) generally perform similarly on TF-IDF cosine similarity features, heavily correlating high similarity scores with the "Good Fit" label. 

## 9. Error Analysis
False Positives (predicted 'Good Fit' when the actual label is 'No Fit') often occur when the resume and JD share high keyword overlap (same domain/industry terminology) but differ in semantic role or seniority (e.g., a "Data Science Intern" applying for a "Lead Data Engineer" position). The TF-IDF model operates purely as a bag-of-words and cannot understand syntax, seniority, or implicit semantic relationships.

## 10. Selected Baseline
**Logistic Regression** was selected as the final baseline due to its comparable performance to SVM, significantly faster training time than Random Forest, and its ability to output calibrated class probabilities (`predict_proba`).

## 11. Limitations
- **Vocabulary Misses:** TF-IDF cannot connect "React" to "Frontend Engineer" unless those exact strings co-occur.
- **Length Biases:** Extremely long JDs tend to dilute the cosine similarity scores of average-length resumes.

## 12. Interface for Phase 5 Comparison
Phase 5 (Sentence-BERT) will independently produce predictions. To ensure a fair comparison:
1. Phase 5 must evaluate on the **exact same official test set** (`ds['test']`).
2. Phase 5 must report the **Macro F1 Score** and per-class F1-scores.
3. Phase 5 must output a classification report matrix to compare against the baseline matrix saved in the Phase 4 notebook. 
4. The output arrays (e.g., `y_pred`) should be saved or analyzed side-by-side on the official test slice.
