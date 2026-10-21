from typing import Dict, Any, List

def generate_candidate_explanation(candidate_data: Dict[str, Any]) -> str:
    """
    Generate an interpretable text explanation based on Phase 6 candidate ranking output.
    
    Expected keys in candidate_data:
    - overall_score
    - recommendation
    - skill_match_percentage
    - matched_skills
    - missing_required_skills
    - score_breakdown (dict with skill_contribution, baseline_text_contribution, semantic_text_contribution)
    """
    score = candidate_data.get("overall_score", 0.0)
    rec = candidate_data.get("recommendation", "Unknown")
    skill_match = candidate_data.get("skill_match_percentage", 0.0)
    matched = candidate_data.get("matched_skills", [])
    missing = candidate_data.get("missing_required_skills", [])
    breakdown = candidate_data.get("score_breakdown", {})
    
    # Back-calculate raw scores if possible, or just show contribution
    # We will show the raw component contributions to the final score
    skill_contrib = breakdown.get("skill_contribution", 0.0)
    baseline_contrib = breakdown.get("baseline_text_contribution", 0.0)
    semantic_contrib = breakdown.get("semantic_text_contribution", 0.0)
    
    lines = []
    lines.append(f"Candidate Score: {score:.1f}/100.0 ({rec})")
    lines.append(f"Skill Match: {skill_match:.1f}%")
    
    lines.append("")
    lines.append("Score Contribution Breakdown:")
    lines.append(f"- Skills Contribution: {skill_contrib:.1f} pts")
    lines.append(f"- Semantic Contribution (Phase 5): {semantic_contrib:.1f} pts")
    lines.append(f"- Baseline Contribution (Phase 4): {baseline_contrib:.1f} pts")
    
    lines.append("")
    lines.append("Matched Skills:")
    if matched:
        for s in matched:
            lines.append(f"- {s}")
    else:
        lines.append("- None")
        
    lines.append("")
    lines.append("Missing Required Skills:")
    if missing:
        for s in missing:
            lines.append(f"- {s}")
    else:
        lines.append("- None")
        
    lines.append("")
    lines.append("Summary:")
    if skill_match >= 80:
        lines.append("- Strong required-skill coverage.")
    elif skill_match >= 50:
        lines.append("- Moderate required-skill coverage.")
    else:
        lines.append("- Lacks critical required skills.")
        
    # Analyze text scores vs weights
    weights = breakdown.get("weights_used", {})
    sem_weight = weights.get("semantic_match", 0) * 100
    
    if sem_weight > 0 and semantic_contrib / (sem_weight + 1e-9) > 0.7:
        lines.append("- High semantic similarity to job description.")
    elif sem_weight > 0 and semantic_contrib / (sem_weight + 1e-9) < 0.4:
        lines.append("- Weak semantic alignment with job description.")
        
    return "\n".join(lines)
