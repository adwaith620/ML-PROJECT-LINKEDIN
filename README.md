# TalentLens — Resume Screening & Skill Gap Analysis System

TalentLens is an intelligent, easy-to-use recruitment tool built with Machine Learning and Natural Language Processing (NLP). It helps recruiters compare a candidate's resume with a job description to quickly see how well their skills match, identify missing requirements, and view real evidence extracted directly from the resume.

---

## 👥 Team MembersT

* **Adwaith Krishna M H**
* **Adwaith HA**
* **Abhinand JS**
* **Siya S**
* **Afraaz S M**

---

## 🚀 Key Features

* **Upload Resumes & Job Descriptions:** Supports PDF, Microsoft Word (`.docx`), and plain text (`.txt`) documents, or paste job descriptions directly.
* **Smart Skill Matching:** Recognizes technical skills, tool aliases (like `k8s` for Kubernetes, `AWS` for Amazon Web Services), and related technologies (like giving partial credit for PostgreSQL when MySQL is required).
* **Section-Aware Analysis:** Understands the difference between "Must-Have" requirements and "Nice-to-Have" preferred qualifications.
* **Verified Resume Evidence:** Shows the exact sentences from the candidate's work experience or projects where each skill was demonstrated, avoiding repetitive lists.
* **Transparent Compatibility Score:** Provides an overall compatibility percentage and an easy-to-understand breakdown showing how skills and text similarity contributed to the final score.
* **PDF & JSON Reports:** Download a professionally formatted PDF summary report with one click or export structured JSON data.
* **Light & Dark Mode:** Accessible, high-contrast dark and light themes that remember your preference.
* **100% Local & Private:** Runs entirely on your machine. No resumes or personal data are ever sent to external cloud APIs or stored permanently.

---

## 🛠️ How It Works

1. **Document Reading & Text Cleaning:** Extracts text from uploaded PDF or Word files while preserving technical terms like `C++`, `C#`, `.NET`, `CI/CD`, and `Python 3`.
2. **Skill Extraction & Matching:** Scans the text against a dictionary of technical skills and categorizes each requirement into:
   * **Exact Match:** Found directly in the resume.
   * **Recognized Alias:** Found using an alternative name or abbreviation.
   * **Related Skill:** The candidate has an equivalent skill in the same domain.
   * **Missing:** Not evidenced in the resume.
3. **Similarity Analysis:** Combines keyword overlap (TF-IDF) with deep semantic understanding using Sentence-BERT (`all-MiniLM-L6-v2`) to capture context and role alignment.
4. **Scoring:** Calculates a fair, weighted compatibility score based on required skills coverage, text similarity, and any preferred bonus skills.

---

## 💻 Quickstart (Running Locally)

### Prerequisites
* **Python 3.11+** installed
* **Node.js (v18+)** and `npm` installed

### 1. Clone the Repository
```bash
git clone https://github.com/adwaith620/ML-PROJECT-LINKEDIN.git
cd ML-PROJECT-LINKEDIN
