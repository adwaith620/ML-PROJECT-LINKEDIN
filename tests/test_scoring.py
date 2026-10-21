import pytest
from src.scoring.skill_gap import normalize_skill, analyze_skill_gap
from src.scoring.candidate_score import calculate_candidate_score, determine_recommendation
from src.scoring.ranking import rank_candidates

def test_skill_normalization():
    assert normalize_skill("ML") == "machine learning"
    assert normalize_skill("Machine-Learning") == "machine learning"
    assert normalize_skill(" Python ") == "python"
    assert normalize_skill("") == ""
    assert normalize_skill(None) == ""

def test_skill_gap_analysis():
    req = ["Python", "SQL", "AWS"]
    opt = ["Docker", "Kubernetes"]
    
    # Perfect match + additional
    cand1 = ["Python", "sql", "aws", "Docker", "Git"]
    gap1 = analyze_skill_gap(cand1, req, opt)
    
    assert gap1["match_percentage"] == 100.0
    assert "git" in gap1["additional_skills"]
    assert "docker" in gap1["matched_optional"]
    assert len(gap1["missing_required"]) == 0
    
    # Zero match
    cand2 = ["Java", "C++"]
    gap2 = analyze_skill_gap(cand2, req, opt)
    assert gap2["match_percentage"] == 0.0
    assert "python" in gap2["missing_required"]
    
    # Empty requirements
    gap3 = analyze_skill_gap(["Java"], [], [])
    assert gap3["match_percentage"] == 100.0

def test_candidate_scoring_no_semantic():
    score = calculate_candidate_score(
        skill_match_percentage=100.0,
        baseline_text_score=0.5,
        semantic_score=None
    )
    # Weights: 60% skills, 40% baseline
    expected = (100.0 * 0.6) + (50.0 * 0.4)
    assert score["overall_score"] == expected
    assert score["recommendation"] == "Strong Match"

def test_candidate_scoring_with_semantic():
    score = calculate_candidate_score(
        skill_match_percentage=100.0,
        baseline_text_score=0.5,
        semantic_score=0.8
    )
    # Weights: 40% skills, 20% baseline, 40% semantic
    expected = (100.0 * 0.4) + (50.0 * 0.2) + (80.0 * 0.4)
    assert score["overall_score"] == expected
    assert score["recommendation"] == "Strong Match"
    
def test_recommendation_thresholds():
    assert determine_recommendation(100.0) == "Strong Match"
    assert determine_recommendation(80.0) == "Strong Match"
    assert determine_recommendation(79.9) == "Moderate Match"
    assert determine_recommendation(60.0) == "Moderate Match"
    assert determine_recommendation(45.0) == "Potential Match"
    assert determine_recommendation(39.0) == "Low Match"

def test_ranking():
    job = {
        "required_skills": ["Python", "ML"],
        "optional_skills": ["AWS"]
    }
    
    candidates = [
        {"candidate_id": "C1", "candidate_skills": ["Python"], "baseline_match_score": 0.5},
        {"candidate_id": "C2", "candidate_skills": ["Python", "ML", "AWS"], "baseline_match_score": 0.8},
        {"candidate_id": "C3", "candidate_skills": ["Java"], "baseline_match_score": 0.1}
    ]
    
    ranked = rank_candidates(candidates, job)
    
    assert len(ranked) == 3
    assert ranked[0]["candidate_id"] == "C2"  # 100% skill match + 0.8 baseline
    assert ranked[1]["candidate_id"] == "C1"  # 50% skill match + 0.5 baseline
    assert ranked[2]["candidate_id"] == "C3"  # 0% skill match + 0.1 baseline
    
    # Check structure
    assert "matched_skills" in ranked[0]
    assert "missing_required_skills" in ranked[0]
    assert "score_breakdown" in ranked[0]
