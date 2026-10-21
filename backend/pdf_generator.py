"""
pdf_generator.py

Professional PDF report generator using ReportLab.
Produces structured, publication-quality compatibility reports for candidates.
"""

import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_str)
        self.drawString(54, 36, "TalentLens — Resume Screening & Skill Gap Analysis System | Confidential Report")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()


def generate_pdf_report(analysis_result: Dict[str, Any]) -> bytes:
    """
    Generates a PDF document from an analysis result dictionary.
    Returns the binary content of the PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e293b")  # slate 800
    accent_color = colors.HexColor("#2563eb")   # blue 600
    border_color = colors.HexColor("#cbd5e1")   # slate 300
    bg_light = colors.HexColor("#f8fafc")       # slate 50

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    body_bold = ParagraphStyle(
        "BodyBoldCustom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=primary_color,
    )
    score_style = ParagraphStyle(
        "ScoreBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=30,
        textColor=accent_color,
        alignment=1,  # Center
    )
    score_label_style = ParagraphStyle(
        "ScoreLabel",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748b"),
    )

    story = []

    # 1. Header & Title
    story.append(Paragraph("Candidate Compatibility & Skill Gap Report", title_style))
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on {current_time} | Report ID: {analysis_result.get('request_id', 'N/A')[:8]}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceBefore=4, spaceAfter=14))

    # 2. Executive Summary Box
    score = analysis_result.get("overall_score", 0.0)
    recommendation = analysis_result.get("recommendation", "N/A")
    method = analysis_result.get("analysis_method", "N/A")
    resume_file = analysis_result.get("resume_filename", "Uploaded Resume")
    jd_file = analysis_result.get("jd_filename", "Job Description")

    score_cell = [
        Paragraph(f"{score:.1f}%", score_style),
        Paragraph("Compatibility Score", score_label_style),
        Spacer(1, 4),
        Paragraph(f"<b>Classification:</b> {recommendation}", ParagraphStyle("Rec", parent=body_style, alignment=1)),
    ]

    details_cell = [
        Paragraph(f"<b>Candidate Resume:</b> {resume_file}", body_style),
        Spacer(1, 3),
        Paragraph(f"<b>Job Description:</b> {jd_file}", body_style),
        Spacer(1, 3),
        Paragraph(f"<b>Active Method:</b> {method}", body_style),
        Spacer(1, 3),
        Paragraph(f"<b>Required Skills Coverage:</b> {analysis_result.get('required_skills_matched', 0)} of {analysis_result.get('required_skills_total', 0)} ({analysis_result.get('skill_match_percentage', 0):.1f}%)", body_style),
    ]

    summary_table = Table([[details_cell, score_cell]], colWidths=[350, 154])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('LINEAFTER', (0, 0), (0, -1), 1, border_color),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Score Component Breakdown Table
    story.append(Paragraph("Score Component Breakdown", h2_style))
    breakdown = analysis_result.get("score_breakdown", {})
    weights = breakdown.get("weights_used", {})

    breakdown_data = [
        [Paragraph("Component", body_bold), Paragraph("Weight", body_bold), Paragraph("Calculated Input", body_bold), Paragraph("Contribution", body_bold)],
        [
            Paragraph("Structured Skill Coverage", body_style),
            Paragraph(f"{weights.get('skill_match', 0)*100:.0f}%", body_style),
            Paragraph(f"{analysis_result.get('skill_match_percentage', 0):.1f}%", body_style),
            Paragraph(f"{breakdown.get('skill_contribution', 0):.1f} pts", body_style)
        ],
        [
            Paragraph("Lexical Baseline (TF-IDF)", body_style),
            Paragraph(f"{weights.get('text_baseline', 0)*100:.0f}%", body_style),
            Paragraph(f"{analysis_result.get('lexical_similarity', 0)*100:.1f}%", body_style),
            Paragraph(f"{breakdown.get('baseline_text_contribution', 0):.1f} pts", body_style)
        ],
    ]

    sem_val = analysis_result.get("semantic_similarity")
    if sem_val is not None:
        breakdown_data.append([
            Paragraph("Semantic Similarity (Sentence-BERT)", body_style),
            Paragraph(f"{weights.get('semantic_match', 0)*100:.0f}%", body_style),
            Paragraph(f"{sem_val*100:.1f}%", body_style),
            Paragraph(f"{breakdown.get('semantic_text_contribution', 0):.1f} pts", body_style)
        ])

    breakdown_data.append([
        Paragraph("<b>Total Compatibility Score</b>", body_style),
        Paragraph("<b>100%</b>", body_style),
        Paragraph("-", body_style),
        Paragraph(f"<b>{score:.1f} / 100.0</b>", body_style)
    ])

    b_table = Table(breakdown_data, colWidths=[200, 80, 110, 114])
    b_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, primary_color),
    ]))
    story.append(b_table)
    story.append(Spacer(1, 14))

    # 4. Matched Skills & Genuine Evidence
    story.append(Paragraph("Matched Skills (Found in Both Resume & Job Description)", h2_style))
    matched_skills = analysis_result.get("matched_skills", [])
    if matched_skills:
        skill_rows = [[Paragraph("Matched Skill", body_bold), Paragraph("Evidence Snippet from Resume", body_bold)]]
        for m in matched_skills:
            skill_name = m.get("skill", "") if isinstance(m, dict) else str(m)
            evidence_list = m.get("evidence", []) if isinstance(m, dict) else []
            ev_text = " \"".join(evidence_list)
            if evidence_list:
                ev_p = Paragraph(f"<i>\"{evidence_list[0]}\"</i>", body_style)
            else:
                ev_p = Paragraph("<font color='#64748b'>Identified via technical term match</font>", body_style)

            skill_rows.append([
                Paragraph(f"<b>{skill_name}</b>", body_style),
                ev_p
            ])

        m_table = Table(skill_rows, colWidths=[140, 364])
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(m_table)
    else:
        story.append(Paragraph("<i>No overlapping required skills were detected.</i>", body_style))

    story.append(Spacer(1, 14))

    # 5. Missing / Unevidenced Required Skills
    missing_skills = analysis_result.get("missing_required_skills", [])
    story.append(Paragraph("Missing or Unevidenced Required Skills", h2_style))
    if missing_skills:
        missing_text = ", ".join(missing_skills)
        story.append(Paragraph(
            f"The following skills were explicitly identified in the job description but not detected in the candidate's resume: <b>{missing_text}</b>. "
            f"<font color='#64748b'>(Note: The absence of a term in the resume indicates it was unevidenced, not necessarily that the candidate lacks the competency.)</font>",
            body_style
        ))
    else:
        story.append(Paragraph("<i>All identified job requirements were evidenced in the candidate's resume.</i>", body_style))

    story.append(Spacer(1, 14))

    # 6. Additional Skills
    additional_skills = analysis_result.get("additional_skills", [])
    if additional_skills:
        story.append(Paragraph("Additional Candidate Skills (Not explicitly required by JD)", h2_style))
        story.append(Paragraph(
            f"The candidate also evidenced the following competencies: <b>{', '.join(additional_skills)}</b>.",
            body_style
        ))
        story.append(Spacer(1, 14))

    # 7. Extracted Qualifications & Background
    exp = analysis_result.get("experience_findings", [])
    edu = analysis_result.get("education_findings", [])
    certs = analysis_result.get("certifications_findings", [])
    if exp or edu or certs:
        story.append(Paragraph("Extracted Candidate Background", h2_style))
        bg_items = []
        if exp:
            bg_items.append(f"<b>Stated Experience:</b> {', '.join(exp)}")
        if edu:
            bg_items.append(f"<b>Education:</b> {', '.join(edu)}")
        if certs:
            bg_items.append(f"<b>Certifications:</b> {', '.join(certs)}")
        for item in bg_items:
            story.append(Paragraph(item, body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 10))

    # 8. Warnings and Extraction Quality Notes
    warnings = analysis_result.get("warnings", [])
    if warnings:
        story.append(Paragraph("Quality Notes & Warnings", h2_style))
        for w in warnings:
            story.append(Paragraph(f"• {w}", body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 10))

    # 9. Methodology & Ethical Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=8, spaceAfter=8))
    story.append(Paragraph(
        "<b>Notice and Methodology:</b> This compatibility assessment was calculated automatically using natural language "
        "processing (NLP), TF-IDF lexical matching, and Sentence-BERT semantic representation. It is provided strictly for "
        "recruiter decision support and prioritization. It does not predict future job performance, nor should it serve as "
        "the sole basis for employment decisions. All data processed in temporary memory and retained in compliance with local privacy policies.",
        disclaimer_style
    ))

    # Build document with custom canvas for page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
