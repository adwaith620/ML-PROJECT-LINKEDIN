import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  Download,
  Copy,
  RotateCcw,
  Layers,
  FileCheck,
  X,
  FileUp,
  Sun,
  Moon,
  Zap,
  Sparkles,
  Info,
} from 'lucide-react';
import { AnalysisResult, BackendHealth } from './types';
import './styles.css';

export const App: React.FC = () => {
  // State
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState<string>('');
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [preferredMethod, setPreferredMethod] = useState<string>('auto');

  const [loading, setLoading] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<string>('');
  const [stageProgress, setStageProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [copyFeedback, setCopyFeedback] = useState<boolean>(false);

  // Accessible Dark Mode state with persistence & system preference fallback
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const savedTheme = localStorage.getItem('talentlens_theme');
    if (savedTheme === 'dark') return true;
    if (savedTheme === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const jdFileInputRef = useRef<HTMLInputElement>(null);

  // Sync theme changes to body class and localStorage
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-theme');
      localStorage.setItem('talentlens_theme', 'dark');
    } else {
      document.body.classList.remove('dark-theme');
      localStorage.setItem('talentlens_theme', 'light');
    }
  }, [isDarkMode]);

  // Listen for OS system theme changes if user has not set a preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('talentlens_theme')) {
        setIsDarkMode(e.matches);
      }
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Check backend health on mount
  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : null))
      .then((data: BackendHealth | null) => {
        if (data) setHealth(data);
      })
      .catch((err) => {
        console.warn('Backend health check error:', err);
      });
  }, []);

  // Drag and drop handling
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetResume(e.dataTransfer.files[0]);
    }
  };

  const validateAndSetResume = (file: File) => {
    setError(null);
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError(`Unsupported file type '${ext}'. Please upload a PDF, DOCX, or TXT file.`);
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setError(`File exceeds the 25 MB size limit (${(file.size / (1024 * 1024)).toFixed(2)} MB).`);
      return;
    }

    setResumeFile(file);
  };

  const handleJdFileUpload = (file: File) => {
    setError(null);
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError(`Unsupported job description document '${ext}'. Please select a PDF, DOCX, or TXT file.`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError(`JD document exceeds the 10 MB size limit.`);
      return;
    }

    setJdFile(file);
  };

  // Submit Analysis
  const handleAnalyze = async () => {
    if (!resumeFile) {
      setError('Please provide a candidate resume.');
      return;
    }

    if (!jdText.trim() && !jdFile) {
      setError('Please paste a job description or upload a JD document.');
      return;
    }

    setError(null);
    setLoading(true);
    setAnalysisResult(null);

    // Staged progress updates
    setCurrentStage('Uploading document to analysis engine...');
    setStageProgress(20);

    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    if (jdFile) {
      formData.append('jd_file', jdFile);
    } else {
      formData.append('jd_text', jdText);
    }
    formData.append('preferred_method', preferredMethod);

    try {
      const stageTimer1 = setTimeout(() => {
        setCurrentStage('Extracting document text and parsing requirements...');
        setStageProgress(45);
      }, 500);

      const stageTimer2 = setTimeout(() => {
        setCurrentStage('Classifying exact, alias & related skills and computing ML embeddings...');
        setStageProgress(75);
      }, 1200);

      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `Server error (${res.status})`);
      }

      setCurrentStage('Finalizing compatibility report...');
      setStageProgress(100);

      const data: AnalysisResult = await res.json();
      setAnalysisResult(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
      setCurrentStage('');
      setStageProgress(0);
    }
  };

  // Download PDF
  const handleDownloadPdf = async () => {
    if (!analysisResult) return;

    try {
      const res = await fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisResult),
      });

      if (!res.ok) throw new Error('Failed to generate PDF');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `TalentLens_Report_${analysisResult.request_id.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(`Could not download PDF: ${err.message}`);
    }
  };

  // Export JSON
  const handleExportJson = () => {
    if (!analysisResult) return;
    const jsonStr = JSON.stringify(analysisResult, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TalentLens_${analysisResult.request_id.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Copy Summary
  const handleCopySummary = () => {
    if (!analysisResult) return;
    const matched = analysisResult.matched_skills.map((m) => {
      if (m.is_related) {
        return `${m.skill} (via ${m.candidate_related_skill}, ${(m.transferable_credit || 0.5) * 100}%)`;
      }
      return m.skill;
    }).join(', ') || 'None';
    const missing = analysisResult.missing_required_skills.join(', ') || 'None';
    const additional = analysisResult.additional_skills.join(', ') || 'None';

    const text = `Candidate Compatibility Summary
Candidate File: ${analysisResult.resume_filename}
Job Description: ${analysisResult.jd_filename}
Overall Score: ${analysisResult.overall_score}% (${analysisResult.recommendation})
Active Method: ${analysisResult.analysis_method}
Required Skills Coverage: ${analysisResult.required_skills_matched}/${analysisResult.required_skills_total} (${analysisResult.skill_match_percentage}%)
Matched Skills: ${matched}
Missing Required Skills: ${missing}
Additional Skills: ${additional}`;

    navigator.clipboard.writeText(text);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2500);
  };

  // Reset form
  const handleReset = () => {
    setResumeFile(null);
    setAnalysisResult(null);
    setError(null);
  };

  const getRecommendationTagClass = (rec: string) => {
    switch (rec) {
      case 'Strong Match':
        return 'tag-strong';
      case 'Moderate Match':
        return 'tag-moderate';
      case 'Potential Match':
        return 'tag-potential';
      default:
        return 'tag-low';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatEvidenceCategory = (category?: string) => {
    switch (category) {
      case 'work_experience':
        return 'Work Experience';
      case 'projects':
        return 'Projects';
      case 'education_certification':
        return 'Education & Certifications';
      case 'skills_list':
        return 'Skills Inventory';
      default:
        return 'Document Text';
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo" aria-hidden="true">TL</div>
          <div>
            <h1 className="brand-title">TalentLens</h1>
            <p className="brand-subtitle">Resume Screening & Skill Gap Analysis System</p>
          </div>
        </div>

        <div className="header-controls">
          {/* Dark Mode Toggle Button */}
          <button
            type="button"
            className="theme-toggle-btn"
            onClick={() => setIsDarkMode((prev) => !prev)}
            aria-label={isDarkMode ? 'Switch to light theme' : 'Switch to dark theme'}
            title={isDarkMode ? 'Switch to light theme' : 'Switch to dark theme'}
          >
            {isDarkMode ? <Sun size={15} /> : <Moon size={15} />}
            <span>{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
          </button>

          {/* Backend Status Indicator */}
          <div className="header-status">
            <div className={`status-dot ${health?.status === 'healthy' ? 'active' : ''}`} />
            <span>
              {health?.status === 'healthy'
                ? `Local Engine (${health.models.sentence_bert.ready ? 'Sentence-BERT Active' : 'TF-IDF Baseline'})`
                : 'Connecting to Engine...'}
            </span>
          </div>
        </div>
      </header>

      {/* Global Error Alert */}
      {error && (
        <div className="alert-error" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Analysis Input Form */}
      {!analysisResult && (
        <>
          <div className="workspace-grid">
            {/* Panel 1: Resume Upload */}
            <div className="panel-card">
              <div className="panel-header">
                <div>
                  <h2 className="panel-title">1. Candidate Resume</h2>
                  <p className="panel-desc">Upload candidate resume in PDF, DOCX, or TXT format.</p>
                </div>
                <span className="limit-badge">Max 25 MB • 100 pgs</span>
              </div>

              {!resumeFile ? (
                <div
                  className={`dropzone ${isDragOver ? 'active' : ''}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => resumeInputRef.current?.click()}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      resumeInputRef.current?.click();
                    }
                  }}
                  aria-label="Upload Candidate Resume"
                >
                  <Upload className="dropzone-icon" size={32} />
                  <p className="dropzone-text">Click to browse or drag and drop resume</p>
                  <p className="dropzone-subtext">PDF, DOCX, or TXT up to 25 MB</p>
                  <input
                    ref={resumeInputRef}
                    type="file"
                    style={{ display: 'none' }}
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        validateAndSetResume(e.target.files[0]);
                      }
                    }}
                  />
                </div>
              ) : (
                <div className="file-selected-box">
                  <div className="file-info">
                    <FileText size={28} color="var(--color-accent)" />
                    <div>
                      <div className="file-name">{resumeFile.name}</div>
                      <div className="file-size">{formatFileSize(resumeFile.size)}</div>
                    </div>
                  </div>
                  <button
                    className="btn-remove"
                    title="Remove file"
                    aria-label="Remove resume file"
                    onClick={() => setResumeFile(null)}
                  >
                    <X size={18} />
                  </button>
                </div>
              )}
            </div>

            {/* Panel 2: Job Description */}
            <div className="panel-card">
              <div className="panel-header">
                <div>
                  <h2 className="panel-title">2. Job Description</h2>
                  <p className="panel-desc">Paste the job posting text or upload a job document.</p>
                </div>
                <span className="limit-badge">Max 10 MB</span>
              </div>

              {jdFile ? (
                <div className="file-selected-box" style={{ marginBottom: 12 }}>
                  <div className="file-info">
                    <FileCheck size={26} color="var(--color-success)" />
                    <div>
                      <div className="file-name">{jdFile.name}</div>
                      <div className="file-size">{formatFileSize(jdFile.size)} (Document Attached)</div>
                    </div>
                  </div>
                  <button
                    className="btn-remove"
                    title="Remove JD file"
                    aria-label="Remove JD document"
                    onClick={() => setJdFile(null)}
                  >
                    <X size={18} />
                  </button>
                </div>
              ) : (
                <textarea
                  className="jd-textarea"
                  placeholder="Paste the job description here... (e.g., Senior Python Developer required. Must have strong skills in Python, FastAPI, Docker, and PostgreSQL. Preferred: Kubernetes, Redis...)"
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  disabled={loading}
                  aria-label="Job description text"
                />
              )}

              <div className="jd-footer">
                <div>
                  {!jdFile && (
                    <span>
                      {jdText.length} characters • {jdText.split(/\s+/).filter(Boolean).length} words
                    </span>
                  )}
                </div>
                <div>
                  <input
                    ref={jdFileInputRef}
                    type="file"
                    style={{ display: 'none' }}
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleJdFileUpload(e.target.files[0]);
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="btn-file-alt"
                    onClick={() => jdFileInputRef.current?.click()}
                  >
                    <FileUp size={14} />
                    <span>{jdFile ? 'Replace JD Document' : 'Upload JD Document instead'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Action Bar */}
          <div className="action-bar">
            <div className="method-select-group">
              <label htmlFor="method-select">Matching Methodology:</label>
              <select
                id="method-select"
                className="method-select"
                value={preferredMethod}
                onChange={(e) => setPreferredMethod(e.target.value)}
                disabled={loading}
              >
                <option value="auto">Sentence-BERT + Classical TF-IDF (Hybrid)</option>
                <option value="semantic">Sentence-BERT Only</option>
                <option value="classical">Classical Baseline (TF-IDF)</option>
              </select>
            </div>

            <button
              className="btn-primary"
              disabled={loading || !resumeFile || (!jdText.trim() && !jdFile)}
              onClick={handleAnalyze}
            >
              <Layers size={16} />
              <span>{loading ? 'Analyzing...' : 'Analyse Compatibility'}</span>
            </button>
          </div>

          {/* Honest Stage Progress Tracker */}
          {loading && (
            <div className="progress-card">
              <div className="stage-label">{currentStage}</div>
              <div className="stage-subtext">Executing NLP & ML pipeline locally...</div>
              <div className="progress-track">
                <div className="progress-bar-fill" style={{ width: `${stageProgress}%` }} />
              </div>
            </div>
          )}
        </>
      )}

      {/* Results View */}
      {analysisResult && (
        <div className="results-container">
          {/* Action Header */}
          <div className="report-action-header">
            <div className="report-title-group">
              <h2>Candidate Evaluation Report</h2>
              <p>
                Resume: <b>{analysisResult.resume_filename}</b> vs. <b>{analysisResult.jd_filename}</b>
              </p>
            </div>

            <div className="action-buttons">
              <button className="btn-secondary" onClick={handleDownloadPdf} title="Download ReportLab PDF">
                <Download size={15} />
                <span>Download PDF</span>
              </button>
              <button className="btn-secondary" onClick={handleExportJson} title="Export Structured JSON">
                <FileText size={15} />
                <span>Export JSON</span>
              </button>
              <button className="btn-secondary" onClick={handleCopySummary} title="Copy Summary Text">
                <Copy size={15} />
                <span>{copyFeedback ? 'Copied!' : 'Copy Summary'}</span>
              </button>
              <button className="btn-primary" onClick={handleReset}>
                <RotateCcw size={15} />
                <span>Analyze Another Candidate</span>
              </button>
            </div>
          </div>

          {/* Overview Card */}
          <div className="score-overview-card">
            <div className="score-visual-pane">
              <div className="score-circle">{analysisResult.overall_score.toFixed(1)}%</div>
              <span className="stat-label">Compatibility Score</span>
              <span className={`score-badge-tag ${getRecommendationTagClass(analysisResult.recommendation)}`}>
                {analysisResult.recommendation}
              </span>
            </div>

            <div className="score-details-pane">
              <div className="stat-item">
                <span className="stat-label">Required Skills Coverage</span>
                <span className="stat-value">
                  {analysisResult.required_skills_matched} of {analysisResult.required_skills_total} ({analysisResult.skill_match_percentage.toFixed(0)}%)
                </span>
                {analysisResult.coverage_metrics && analysisResult.coverage_metrics.related_matched_count > 0 && (
                  <span style={{ fontSize: 11, color: 'var(--color-related)', marginTop: 2 }}>
                    +{analysisResult.coverage_metrics.related_matched_count} related skill (
                    {analysisResult.coverage_metrics.effective_matched_units.toFixed(1)} effective units)
                  </span>
                )}
              </div>

              <div className="stat-item">
                <span className="stat-label">Lexical Similarity (TF-IDF)</span>
                <span className="stat-value">{(analysisResult.lexical_similarity * 100).toFixed(1)}%</span>
              </div>

              <div className="stat-item">
                <span className="stat-label">Semantic Similarity (Sentence-BERT)</span>
                <span className="stat-value">
                  {analysisResult.semantic_similarity !== null
                    ? `${(analysisResult.semantic_similarity * 100).toFixed(1)}%`
                    : 'N/A (Classical mode)'}
                </span>
              </div>

              <div className="stat-item">
                <span className="stat-label">Active Model Engine</span>
                <span className="stat-value" style={{ fontSize: 13 }}>
                  {analysisResult.analysis_method}
                </span>
              </div>
            </div>
          </div>

          {/* Section Parsing Notice */}
          {analysisResult.section_certainty && (
            <div className="alert-info">
              <Info size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
              <span>
                {analysisResult.section_certainty === 'explicit'
                  ? 'Job description sections (Required vs. Preferred qualifications) were identified from explicit document headers.'
                  : 'Job description requirements were classified using contextual cues (no explicit headers found).'}
              </span>
            </div>
          )}

          {/* Score Component Breakdown Table */}
          <div className="skills-card">
            <h3 className="panel-title">Score Component Breakdown</h3>
            <p className="panel-desc">Inspect how each weighted ML component contributes to the final score.</p>

            <table className="breakdown-table">
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Weight</th>
                  <th>Raw Metric</th>
                  <th>Contribution to Score</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Structured Skill Match Coverage</td>
                  <td>{(analysisResult.score_breakdown.weights_used.skill_match * 100).toFixed(0)}%</td>
                  <td>{analysisResult.skill_match_percentage.toFixed(1)}%</td>
                  <td>{analysisResult.score_breakdown.skill_contribution.toFixed(1)} pts</td>
                </tr>
                <tr>
                  <td>Lexical Baseline (TF-IDF Cosine Similarity)</td>
                  <td>{(analysisResult.score_breakdown.weights_used.text_baseline * 100).toFixed(0)}%</td>
                  <td>{(analysisResult.lexical_similarity * 100).toFixed(1)}%</td>
                  <td>{analysisResult.score_breakdown.baseline_text_contribution.toFixed(1)} pts</td>
                </tr>
                {analysisResult.semantic_similarity !== null && (
                  <tr>
                    <td>Semantic Similarity (Sentence-BERT all-MiniLM-L6-v2)</td>
                    <td>{(analysisResult.score_breakdown.weights_used.semantic_match * 100).toFixed(0)}%</td>
                    <td>{(analysisResult.semantic_similarity * 100).toFixed(1)}%</td>
                    <td>{analysisResult.score_breakdown.semantic_text_contribution.toFixed(1)} pts</td>
                  </tr>
                )}
                {analysisResult.score_breakdown.preferred_skill_bonus !== undefined &&
                  analysisResult.score_breakdown.preferred_skill_bonus > 0 && (
                    <tr>
                      <td>Preferred Skills Bonus (Desirable Qualifications)</td>
                      <td>Bonus (up to 5.0 pts)</td>
                      <td>
                        {analysisResult.coverage_metrics?.preferred_skills_matched_count || 0} preferred skills evidenced
                      </td>
                      <td>+{analysisResult.score_breakdown.preferred_skill_bonus.toFixed(1)} pts</td>
                    </tr>
                  )}
                <tr className="total-row">
                  <td>Total Compatibility Score</td>
                  <td>100%</td>
                  <td>—</td>
                  <td>{analysisResult.overall_score.toFixed(1)} / 100.0</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Matched Required Skills with Evidence & Multi-Tier Classification */}
          <div className="skills-card">
            <div className="panel-header">
              <div>
                <h3 className="panel-title">
                  Matched Required Skills ({analysisResult.matched_skills.length})
                </h3>
                <p className="panel-desc">
                  Required competencies from the job description that were evidenced in the candidate's resume, classified by match type.
                </p>
              </div>
              <span className="limit-badge" style={{ color: 'var(--color-success)', background: 'var(--color-success-light)' }}>
                {analysisResult.skill_match_percentage.toFixed(0)}% Match
              </span>
            </div>

            {analysisResult.matched_skills.length > 0 ? (
              <table className="matched-skills-table">
                <thead>
                  <tr>
                    <th style={{ width: 220 }}>Required Skill & Match Type</th>
                    <th>Prioritized Resume Evidence Snippet</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResult.matched_skills.map((item, idx) => (
                    <tr key={idx}>
                      <td>
                        <span className={`skill-pill ${item.is_related ? 'related' : 'matched'}`}>
                          {item.is_related ? <Zap size={14} /> : <CheckCircle2 size={14} />}
                          <span>{item.skill}</span>
                        </span>
                        
                        <div style={{ marginTop: 4 }}>
                          {item.match_type === 'Exact match' && (
                            <span className="badge-match-type badge-match-exact">Exact Match</span>
                          )}
                          {item.match_type === 'Recognized alias' && (
                            <span className="badge-match-type badge-match-alias">
                              Alias: detected "{item.surface_form_detected || item.skill}"
                            </span>
                          )}
                          {item.is_related && (
                            <span className="badge-match-type badge-match-related">
                              Related Skill ({(item.transferable_credit || 0.5) * 100}% Credit)
                            </span>
                          )}
                        </div>

                        {item.is_related && (
                          <div className="related-callout">
                            Candidate demonstrates <b>{item.candidate_related_skill}</b>.
                            {item.relationship && ` (${item.relationship})`}
                          </div>
                        )}
                      </td>
                      <td>
                        {item.evidence_category && (
                          <div className="badge-evidence-category">
                            {formatEvidenceCategory(item.evidence_category)}
                          </div>
                        )}
                        {item.evidence && item.evidence.length > 0 ? (
                          <div className="evidence-quote">"{item.evidence[0]}"</div>
                        ) : (
                          <span style={{ color: 'var(--color-text-muted)', fontSize: 12 }}>
                            Identified via technical entity recognition
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ color: 'var(--color-text-muted)', fontSize: 13, marginTop: 8 }}>
                No overlapping skills detected between the resume and job requirements.
              </p>
            )}
          </div>

          {/* Missing Required Skills */}
          <div className="skills-card">
            <h3 className="panel-title">
              Missing or Unevidenced Required Skills ({analysisResult.missing_required_skills.length})
            </h3>
            <p className="panel-desc">
              Skills detected in the job posting that were <b>not found or evidenced</b> in the resume text.
              (Note: Absence of a term in the document does not necessarily mean the candidate lacks the skill).
            </p>

            <div className="skills-grid">
              {analysisResult.missing_required_skills.length > 0 ? (
                analysisResult.missing_required_skills.map((skill, idx) => (
                  <span key={idx} className="skill-pill missing">
                    <AlertCircle size={14} />
                    <span>{skill}</span>
                  </span>
                ))
              ) : (
                <span style={{ color: 'var(--color-success)', fontSize: 13, fontWeight: 500 }}>
                  ✓ All required skills from the job description were evidenced in the resume.
                </span>
              )}
            </div>
          </div>

          {/* Preferred Qualifications Section (If detected) */}
          {((analysisResult.matched_preferred && analysisResult.matched_preferred.length > 0) ||
            (analysisResult.missing_preferred_skills && analysisResult.missing_preferred_skills.length > 0)) && (
            <div className="skills-card">
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">
                    <Sparkles size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6, color: 'var(--color-preferred)' }} />
                    Preferred / Desirable Qualifications
                  </h3>
                  <p className="panel-desc">
                    Secondary skills identified from the 'Nice to Have' or 'Preferred' sections. Matched preferred skills provide bonus score points.
                  </p>
                </div>
                <span className="limit-badge" style={{ color: 'var(--color-preferred)', background: 'var(--color-preferred-light)' }}>
                  {analysisResult.matched_preferred?.length || 0} Evidenced
                </span>
              </div>

              {analysisResult.matched_preferred && analysisResult.matched_preferred.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 6 }}>
                    Evidenced Preferred Skills:
                  </div>
                  <div className="skills-grid">
                    {analysisResult.matched_preferred.map((item, idx) => (
                      <span key={idx} className="skill-pill preferred">
                        <CheckCircle2 size={14} />
                        <span>{item.skill}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysisResult.missing_preferred_skills && analysisResult.missing_preferred_skills.length > 0 && (
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: 6 }}>
                    Un-evidenced Preferred Skills:
                  </div>
                  <div className="skills-grid">
                    {analysisResult.missing_preferred_skills.map((skill, idx) => (
                      <span key={idx} className="skill-pill additional">
                        <span>{skill}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Additional Skills */}
          {analysisResult.additional_skills.length > 0 && (
            <div className="skills-card">
              <h3 className="panel-title">
                Additional Skills Evidenced ({analysisResult.additional_skills.length})
              </h3>
              <p className="panel-desc">
                Competencies found in the candidate's resume that were not explicitly listed as job requirements.
              </p>

              <div className="skills-grid">
                {analysisResult.additional_skills.map((skill, idx) => (
                  <span key={idx} className="skill-pill additional">
                    <span>{skill}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Extracted Background */}
          {(analysisResult.experience_findings.length > 0 ||
            analysisResult.education_findings.length > 0 ||
            analysisResult.certifications_findings.length > 0) && (
            <div className="skills-card">
              <h3 className="panel-title">Extracted Candidate Background</h3>
              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13 }}>
                {analysisResult.experience_findings.length > 0 && (
                  <div>
                    <b>Stated Experience:</b> {analysisResult.experience_findings.join(', ')}
                  </div>
                )}
                {analysisResult.education_findings.length > 0 && (
                  <div>
                    <b>Education:</b> {analysisResult.education_findings.join(', ')}
                  </div>
                )}
                {analysisResult.certifications_findings.length > 0 && (
                  <div>
                    <b>Certifications:</b> {analysisResult.certifications_findings.join(', ')}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Quality Warnings */}
          {analysisResult.warnings.length > 0 && (
            <div className="alert-warning" role="note">
              <b>Quality & Extraction Notes:</b>
              <ul style={{ paddingLeft: 18, marginTop: 4 }}>
                {analysisResult.warnings.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
