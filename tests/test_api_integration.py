"""
test_api_integration.py

Integration tests for TalentLens FastAPI backend endpoints.
Tests health checks, configuration, document analysis, PDF exports, and error responses.
"""

import io
import unittest
from fastapi.testclient import TestClient

from backend.main import app


class TestApiIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("models", data)
        self.assertIn("limits", data)
        self.assertEqual(data["limits"]["max_resume_size_bytes"], 25 * 1024 * 1024)

    def test_config_endpoint(self):
        res = self.client.get("/api/config")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["max_resume_size_mb"], 25.0)
        self.assertEqual(data["max_jd_size_mb"], 10.0)
        self.assertIn(".pdf", data["allowed_resume_extensions"])

    def test_analyze_valid_txt_resume_pasted_jd(self):
        resume_bytes = (
            b"Candidate Alex\n"
            b"Software Developer with 4 years of experience in Python, FastAPI, and PostgreSQL.\n"
            b"Education: B.Tech Computer Science\n"
            b"Skills: Python, FastAPI, PostgreSQL, Docker, Git"
        )
        jd_text = (
            "We are hiring a Python Backend Engineer.\n"
            "Requirements: Python, FastAPI, Docker, and Kubernetes.\n"
            "Nice to have: PostgreSQL."
        )

        files = {"resume_file": ("alex_resume.txt", io.BytesIO(resume_bytes), "text/plain")}
        data = {"jd_text": jd_text, "preferred_method": "auto"}

        res = self.client.post("/api/analyze", files=files, data=data)
        self.assertEqual(res.status_code, 200)
        json_data = res.json()

        self.assertEqual(json_data["status"], "success")
        self.assertIn("overall_score", json_data)
        self.assertIn("recommendation", json_data)
        self.assertIn("score_breakdown", json_data)
        self.assertGreaterEqual(json_data["overall_score"], 0.0)
        self.assertLessEqual(json_data["overall_score"], 100.0)

        # Check matched skills (normalized to lower for robust assertion)
        matched_lower = [m["skill"].lower() for m in json_data["matched_skills"]]
        self.assertIn("python", matched_lower)
        self.assertIn("fastapi", matched_lower)
        self.assertIn("docker", matched_lower)

        # Kubernetes was matched via related skill Docker or in missing
        exact_matches = [m["skill"].lower() for m in json_data["matched_skills"] if not m.get("is_related")]
        self.assertNotIn("kubernetes", exact_matches)
        
        # PostgreSQL was in Nice to Have (preferred)
        preferred_matched = [p["skill"].lower() for p in json_data.get("matched_preferred", [])]
        self.assertIn("postgresql", preferred_matched)

    def test_analyze_missing_jd_fails(self):
        resume_bytes = b"Some resume content"
        files = {"resume_file": ("resume.txt", io.BytesIO(resume_bytes), "text/plain")}
        res = self.client.post("/api/analyze", files=files, data={"jd_text": ""})
        self.assertEqual(res.status_code, 400)

    def test_analyze_unsupported_file_fails(self):
        files = {"resume_file": ("malicious.exe", io.BytesIO(b"content"), "application/octet-stream")}
        res = self.client.post("/api/analyze", files=files, data={"jd_text": "Looking for developer"})
        self.assertEqual(res.status_code, 415)

    def test_export_pdf_report(self):
        payload = {
            "request_id": "test-req-001",
            "overall_score": 75.0,
            "recommendation": "Moderate Match",
            "analysis_method": "Sentence-BERT + Classical Hybrid",
            "resume_filename": "candidate.pdf",
            "jd_filename": "job_spec.txt",
            "required_skills_total": 4,
            "required_skills_matched": 3,
            "skill_match_percentage": 75.0,
            "lexical_similarity": 0.60,
            "semantic_similarity": 0.85,
            "score_breakdown": {
                "skill_contribution": 30.0,
                "baseline_text_contribution": 12.0,
                "semantic_text_contribution": 34.0,
                "weights_used": {"skill_match": 0.4, "text_baseline": 0.2, "semantic_match": 0.4}
            },
            "matched_skills": [{"skill": "Python", "evidence": ["Built web scrapers with Python."]}],
            "missing_required_skills": ["Kubernetes"],
            "additional_skills": ["Git", "SQL"],
            "experience_findings": ["4 years"],
            "education_findings": ["B.Tech CS"],
            "certifications_findings": [],
            "warnings": []
        }

        res = self.client.post("/api/export/pdf", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        self.assertTrue(res.content.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
