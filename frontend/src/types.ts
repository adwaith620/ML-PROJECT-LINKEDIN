export interface MatchedSkill {
  skill: string;
  match_type?: 'Exact match' | 'Recognized alias' | 'Related skill' | string;
  surface_form_detected?: string;
  candidate_related_skill?: string;
  relationship?: string;
  transferable_credit?: number;
  evidence: string[];
  evidence_category?: 'work_experience' | 'projects' | 'education_certification' | 'skills_list' | string;
  is_required?: boolean;
  is_related?: boolean;
}

export interface RelatedSkillMatch {
  required_skill: string;
  candidate_related_skill: string;
  relationship: string;
  transferable_credit: number;
  evidence: string[];
  evidence_category: string;
}

export interface PreferredSkillMatch {
  skill: string;
  match_type: string;
  surface_form_detected: string;
  evidence: string[];
  evidence_category: string;
}

export interface CoverageMetrics {
  required_skills_total: number;
  exact_alias_matched_count: number;
  related_matched_count: number;
  effective_matched_units: number;
  skill_coverage_percentage: number;
  preferred_skills_total: number;
  preferred_skills_matched_count: number;
}

export interface ScoreBreakdown {
  skill_contribution: number;
  baseline_text_contribution: number;
  semantic_text_contribution: number;
  preferred_skill_bonus?: number;
  weights_used: {
    skill_match: number;
    text_baseline: number;
    semantic_match: number;
  };
}

export interface DocumentMetadata {
  filename: string;
  format: string;
  file_size_bytes: number;
  extracted_text_bytes: number;
  word_count: number;
  char_count: number;
  unit_count: number;
  is_resume: boolean;
}

export interface AnalysisResult {
  status: string;
  request_id: string;
  resume_filename: string;
  jd_filename: string;
  analysis_method: string;
  overall_score: number;
  recommendation: 'Strong Match' | 'Moderate Match' | 'Potential Match' | 'Low Match' | string;
  required_skills_total: number;
  required_skills_matched: number;
  skill_match_percentage: number;
  matched_skills: MatchedSkill[];
  related_matches?: RelatedSkillMatch[];
  missing_required_skills: string[];
  matched_preferred?: PreferredSkillMatch[];
  missing_preferred_skills?: string[];
  additional_skills: string[];
  semantic_similarity: number | null;
  lexical_similarity: number;
  score_breakdown: ScoreBreakdown;
  coverage_metrics?: CoverageMetrics;
  section_certainty?: 'explicit' | 'inferred' | string;
  detected_sections?: {
    required: boolean;
    preferred: boolean;
    responsibilities: boolean;
    about: boolean;
  };
  experience_findings: string[];
  education_findings: string[];
  certifications_findings: string[];
  roles_findings: string[];
  warnings: string[];
  processing_metadata: {
    resume_meta: DocumentMetadata;
    jd_meta: DocumentMetadata;
    pipeline_version: string;
  };
}

export interface BackendHealth {
  status: string;
  service: string;
  version: string;
  models: {
    sentence_bert: {
      model_name: string;
      ready: boolean;
      status: string;
    };
    baseline_tfidf: {
      ready: boolean;
      status: string;
    };
  };
  limits: {
    max_resume_size_bytes: number;
    max_resume_size_mb: number;
    max_jd_size_bytes: number;
    max_jd_size_mb: number;
    max_pdf_pages: number;
    max_extracted_text_bytes: number;
    max_extracted_text_mb: number;
    processing_timeout_seconds: number;
  };
}
