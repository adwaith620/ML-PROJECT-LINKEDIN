"""Comprehensive test suite for Skill Matching Accuracy, JD Section Parsing,
Multi-tier Classification (Exact, Alias, Related), and Evidence Prioritization.
"""

import unittest
from src.skill_extraction.skill_dictionary import (
    CANONICAL_SKILLS,
    ALIAS_MAP,
    RELATED_SKILLS_MAP,
    normalize_skill,
    get_related_skill_info,
)
from src.skill_extraction.rule_based import extract_skills_rule_based
from src.skill_extraction.jd_parser import parse_job_description
from src.skill_extraction.match_classifier import (
    classify_skill_matches,
    segment_resume_sentences,
    extract_best_evidence_for_skill,
)
from src.scoring.candidate_score import calculate_candidate_score


class TestSkillTaxonomyAndNormalization(unittest.TestCase):
    """Verify centralized taxonomy normalization and alias coverage."""

    def test_python_and_aliases(self):
        self.assertEqual(normalize_skill("python"), "Python")
        self.assertEqual(normalize_skill("Python"), "Python")
        self.assertEqual(normalize_skill("python3"), "Python")
        self.assertEqual(normalize_skill("python 3"), "Python")
        self.assertEqual(normalize_skill("py"), "Python")

    def test_cloud_and_framework_aliases(self):
        self.assertEqual(normalize_skill("k8s"), "Kubernetes")
        self.assertEqual(normalize_skill("aws"), "AWS")
        self.assertEqual(normalize_skill("amazon web services"), "AWS")
        self.assertEqual(normalize_skill("postgres"), "PostgreSQL")
        self.assertEqual(normalize_skill("react.js"), "React")
        self.assertEqual(normalize_skill("reactjs"), "React")
        self.assertEqual(normalize_skill("vue.js"), "Vue.js")
        self.assertEqual(normalize_skill("node"), "Node.js")
        self.assertEqual(normalize_skill("nodejs"), "Node.js")
        self.assertEqual(normalize_skill("sklearn"), "Scikit-Learn")
        self.assertEqual(normalize_skill("scikit learn"), "Scikit-Learn")

    def test_punctuated_technologies(self):
        self.assertIn("c++", ALIAS_MAP)
        self.assertIn("c#", ALIAS_MAP)
        self.assertIn(".net", ALIAS_MAP)
        self.assertIn("ci/cd", ALIAS_MAP)
        self.assertEqual(normalize_skill("c++"), "C++")
        self.assertEqual(normalize_skill("c#"), "C#")
        self.assertEqual(normalize_skill(".net"), ".NET")
        self.assertEqual(normalize_skill("ci/cd"), "CI/CD")

    def test_java_vs_javascript_no_collision(self):
        self.assertEqual(normalize_skill("java"), "Java")
        self.assertEqual(normalize_skill("javascript"), "JavaScript")
        self.assertEqual(normalize_skill("js"), "JavaScript")
        self.assertNotEqual(normalize_skill("java"), normalize_skill("javascript"))


class TestRuleBasedExtractionEdgeCases(unittest.TestCase):
    """Test boundary matching and extraction precision on tricky tech terms."""

    def test_extract_python_in_various_contexts(self):
        text = "We require Python 3 and Python backend engineering with FastAPI."
        extracted = extract_skills_rule_based(text)
        skills = set(extracted)
        self.assertIn("Python", skills)
        self.assertIn("FastAPI", skills)

    def test_punctuated_tech_extraction(self):
        text = "Experienced in C++, C#, .NET, and CI/CD automation pipelines."
        extracted = extract_skills_rule_based(text)
        skills = set(extracted)
        self.assertIn("C++", skills)
        self.assertIn("C#", skills)
        self.assertIn(".NET", skills)
        self.assertIn("CI/CD", skills)

    def test_java_not_extracted_from_javascript(self):
        text = "Front-end specialist with expert JavaScript and React knowledge."
        extracted = extract_skills_rule_based(text)
        skills = set(extracted)
        self.assertIn("JavaScript", skills)
        self.assertIn("React", skills)
        self.assertNotIn("Java", skills)

    def test_sql_and_nosql(self):
        text = "Strong proficiency in SQL queries, PostgreSQL, and NoSQL databases like MongoDB."
        extracted = extract_skills_rule_based(text)
        skills = set(extracted)
        self.assertIn("SQL", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("NoSQL", skills)
        self.assertIn("MongoDB", skills)


class TestJobDescriptionSectionParsing(unittest.TestCase):
    """Test parsing JDs with explicit sections and fallback cue parsing."""

    def test_explicit_sections_separation(self):
        jd_text = """
        Company Overview:
        We are a leading fintech company using Machine Learning and AI to disrupt banking.

        Job Responsibilities:
        - Design and maintain microservices.
        - Build real-time analytics.

        Required Qualifications:
        - 3+ years experience with Python and FastAPI.
        - Solid knowledge of Docker and PostgreSQL.
        - Experience with SQL and Git.

        Preferred Qualifications:
        - Familiarity with Kubernetes and AWS.
        - Experience with Redis caching.
        """
        parsed = parse_job_description(jd_text)
        self.assertEqual(parsed["section_certainty"], "explicit")
        
        req = set(parsed["required_skills"])
        pref = set(parsed["preferred_skills"])
        
        # Required skills
        self.assertIn("Python", req)
        self.assertIn("FastAPI", req)
        self.assertIn("Docker", req)
        self.assertIn("PostgreSQL", req)
        self.assertIn("SQL", req)
        self.assertIn("Git", req)
        
        # Preferred skills
        self.assertIn("Kubernetes", pref)
        self.assertIn("AWS", pref)
        self.assertIn("Redis", pref)
        
        # Preferred skills should NOT be counted as required
        self.assertNotIn("Kubernetes", req)
        self.assertNotIn("AWS", req)
        self.assertNotIn("Redis", req)

        # Contextual skills in about section should not pollute required
        self.assertNotIn("Machine Learning", req)

    def test_inferred_sections_without_headers(self):
        jd_text = (
            "We are looking for a backend developer. "
            "You must have strong skills in Python and Docker. "
            "Ideally, you have knowledge of Kubernetes and AWS. "
            "You will write clean code."
        )
        parsed = parse_job_description(jd_text)
        self.assertEqual(parsed["section_certainty"], "inferred")
        req = set(parsed["required_skills"])
        pref = set(parsed["preferred_skills"])

        self.assertIn("Python", req)
        self.assertIn("Docker", req)
        self.assertIn("Kubernetes", pref)
        self.assertIn("AWS", pref)


class TestMultiTierMatchClassification(unittest.TestCase):
    """Test exact match, alias match, related transferable skills, and not evidenced."""

    def test_exact_and_alias_matches(self):
        resume_skills = [
            {"canonical": "Python", "surface_forms": ["Python"]},
            {"canonical": "Kubernetes", "surface_forms": ["k8s"]},
        ]
        required = ["Python", "Kubernetes", "AWS"]
        
        res = classify_skill_matches(
            resume_skills_dict=resume_skills,
            required_skills=required,
            preferred_skills=[],
            resume_text="Extensive experience in Python and k8s deployments."
        )

        matched_names = {m["skill"]: m for m in res["matched_required"]}
        self.assertIn("Python", matched_names)
        self.assertEqual(matched_names["Python"]["match_type"], "Exact match")
        self.assertEqual(matched_names["Python"]["transferable_credit"], 1.0)

        self.assertIn("Kubernetes", matched_names)
        self.assertEqual(matched_names["Kubernetes"]["match_type"], "Recognized alias")
        self.assertEqual(matched_names["Kubernetes"]["surface_form_detected"], "k8s")

        self.assertIn("AWS", res["missing_required"])

    def test_related_transferable_skills_credit(self):
        # Candidate has PostgreSQL; JD requires MySQL
        resume_skills = [
            {"canonical": "PostgreSQL", "surface_forms": ["PostgreSQL"]},
            {"canonical": "Docker", "surface_forms": ["Docker"]},
        ]
        required = ["MySQL", "Kubernetes"]
        
        res = classify_skill_matches(
            resume_skills_dict=resume_skills,
            required_skills=required,
            preferred_skills=[],
            resume_text="Architected database queries in PostgreSQL and containerized services in Docker."
        )

        related_req_skills = {r["required_skill"]: r for r in res["related_matches"]}
        
        # MySQL matched via PostgreSQL
        self.assertIn("MySQL", related_req_skills)
        self.assertEqual(related_req_skills["MySQL"]["candidate_related_skill"], "PostgreSQL")
        self.assertEqual(related_req_skills["MySQL"]["transferable_credit"], 0.5)

        # Kubernetes matched via Docker
        self.assertIn("Kubernetes", related_req_skills)
        self.assertEqual(related_req_skills["Kubernetes"]["candidate_related_skill"], "Docker")
        self.assertEqual(related_req_skills["Kubernetes"]["transferable_credit"], 0.4)

        # Metrics verify partial credit calculation
        metrics = res["metrics"]
        self.assertEqual(metrics["required_skills_total"], 2)
        self.assertEqual(metrics["exact_alias_matched_count"], 0)
        self.assertEqual(metrics["related_matched_count"], 2)
        # 0.5 + 0.4 = 0.9 effective units out of 2.0 = 45.0%
        self.assertAlmostEqual(metrics["effective_matched_units"], 0.9, places=2)
        self.assertAlmostEqual(metrics["skill_coverage_percentage"], 45.0, places=1)


class TestEvidenceExtractionAndPrioritization(unittest.TestCase):
    """Test prioritizing Work Experience and Projects over generic comma-separated lists."""

    def test_prioritizes_work_experience_over_skills_list(self):
        resume_text = """
        John Doe
        Summary: Software Engineer

        TECHNICAL SKILLS:
        Python, FastAPI, Docker, PostgreSQL, React, Git, AWS, Redis, Linux, Bash

        WORK EXPERIENCE:
        Senior Backend Engineer - Acme Corp (2022 - Present)
        - Developed asynchronous microservices in FastAPI serving 50k requests/sec.
        - Designed real-time pipeline in Python with robust fault tolerance.

        PROJECTS:
        - Built an automated CI/CD pipeline using Docker containers.
        """

        segments = segment_resume_sentences(resume_text)
        
        # Verify section tagging
        work_segs = [s for s in segments if s["section"] == "work_experience"]
        self.assertGreater(len(work_segs), 0)

        # Evidence for FastAPI should come from work experience, not skills list
        fastapi_evidence, category = extract_best_evidence_for_skill(
            canonical_skill="FastAPI",
            segmented_sentences=segments,
            used_snippets=set()
        )
        self.assertEqual(category, "Work Experience")
        self.assertIn("serving 50k requests/sec", fastapi_evidence)

        # Evidence for Docker should come from projects
        docker_evidence, docker_cat = extract_best_evidence_for_skill(
            canonical_skill="Docker",
            segmented_sentences=segments,
            used_snippets=set()
        )
        self.assertEqual(docker_cat, "Project Evidence")
        self.assertIn("Built an automated CI/CD pipeline", docker_evidence)

        # Evidence for Redis (only in skills list) should fall back gracefully to skills section
        redis_evidence, redis_cat = extract_best_evidence_for_skill(
            canonical_skill="Redis",
            segmented_sentences=segments,
            used_snippets=set()
        )
        self.assertEqual(redis_cat, "Skills Section")


class TestScoringTransparencyAndDenominator(unittest.TestCase):
    """Test scoring mechanics, denominators, and preferred bonuses."""

    def test_transparent_breakdown_with_preferred_bonus(self):
        score_res = calculate_candidate_score(
            skill_match_percentage=80.0,
            baseline_text_score=0.70,
            semantic_score=0.85,
            preferred_skill_bonus=4.0
        )
        # Expected:
        # weights = 0.40 skill, 0.20 baseline, 0.40 semantic
        # 0.40 * 80.0 = 32.0 pts
        # 0.20 * 70.0 = 14.0 pts
        # 0.40 * 85.0 = 34.0 pts
        # Base = 80.0
        # Preferred bonus = +4.0
        # Total = 84.0
        self.assertAlmostEqual(score_res["overall_score"], 84.0, places=1)
        self.assertEqual(score_res["recommendation"], "Strong Match")
        self.assertEqual(score_res["score_breakdown"]["preferred_skill_bonus"], 4.0)

    def test_zero_denominator_handled(self):
        # When 0 required skills, skill_match_percentage is 0.0 or handled without division by zero
        score_res = calculate_candidate_score(
            skill_match_percentage=0.0,
            baseline_text_score=0.60,
            semantic_score=0.70
        )
        self.assertGreater(score_res["overall_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
