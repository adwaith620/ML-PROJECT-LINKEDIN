export interface MatchedSkill {
  skill: string;
  evidence: string[];
}

export interface ScoreBreakdown {
  skill_contribution: number;
  baseline_text_contribution: number;
  semantic_text_contribution: number;
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
  missing_required_skills: string[];
  additional_skills: string[];
  semantic_similarity: number | null;
  lexical_similarity: number;
  score_breakdown: ScoreBreakdown;
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
