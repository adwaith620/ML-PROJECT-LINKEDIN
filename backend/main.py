"""
main.py

FastAPI Backend Server for TalentLens Resume Screening and Skill Gap Analysis System.
Provides REST API endpoints for document upload, analysis, health checks, and PDF report export.
"""

import os
import sys
import tempfile
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.resume_parser import (
    MAX_RESUME_SIZE_BYTES,
    MAX_JD_SIZE_BYTES,
    MAX_PDF_PAGES,
    MAX_EXTRACTED_TEXT_BYTES,
    PROCESSING_TIMEOUT_SECONDS,
    ALLOWED_RESUME_EXTENSIONS,
    ALLOWED_JD_EXTENSIONS,
    DocumentParserError,
    FileSizeExceededError,
    PageLimitExceededError,
    TextLengthExceededError,
    UnsupportedFormatError,
    CorruptedDocumentError,
    EncryptedDocumentError,
    EmptyDocumentError,
)
from src.pipeline import (
    analyze_candidate,
    get_semantic_matcher,
    get_baseline_feature_extractor,
)
from backend.pdf_generator import generate_pdf_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("talentlens_backend")

app = FastAPI(
    title="TalentLens API",
    description="Resume Screening and Skill Gap Analysis System using NLP and Machine Learning",
    version="1.0.0"
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint reporting API status, model readiness, and active limits.
    """
    matcher = get_semantic_matcher()
    semantic_ready = matcher.is_ready()
    baseline_extractor = get_baseline_feature_extractor()
    baseline_ready = (baseline_extractor is not None and getattr(baseline_extractor, "is_fitted", False))

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "TalentLens Backend API",
        "version": "1.0.0",
        "models": {
            "sentence_bert": {
                "model_name": "all-MiniLM-L6-v2",
                "ready": semantic_ready,
                "status": "Ready (loaded)" if semantic_ready else "Cached / Lazy-loadable",
            },
            "baseline_tfidf": {
                "ready": baseline_ready,
                "status": "Ready (pre-trained model loaded)" if baseline_ready else "Fallback available",
            }
        },
        "limits": {
            "max_resume_size_bytes": MAX_RESUME_SIZE_BYTES,
            "max_resume_size_mb": MAX_RESUME_SIZE_BYTES / (1024 * 1024),
            "max_jd_size_bytes": MAX_JD_SIZE_BYTES,
            "max_jd_size_mb": MAX_JD_SIZE_BYTES / (1024 * 1024),
            "max_pdf_pages": MAX_PDF_PAGES,
            "max_extracted_text_bytes": MAX_EXTRACTED_TEXT_BYTES,
            "max_extracted_text_mb": MAX_EXTRACTED_TEXT_BYTES / (1024 * 1024),
            "processing_timeout_seconds": PROCESSING_TIMEOUT_SECONDS,
        }
    }


@app.get("/api/config")
async def get_configuration():
    """Returns runtime configuration and upload constraints for the frontend."""
    return {
        "max_resume_size_mb": MAX_RESUME_SIZE_BYTES / (1024 * 1024),
        "max_jd_size_mb": MAX_JD_SIZE_BYTES / (1024 * 1024),
        "max_pdf_pages": MAX_PDF_PAGES,
        "max_extracted_text_mb": MAX_EXTRACTED_TEXT_BYTES / (1024 * 1024),
        "allowed_resume_extensions": sorted(list(ALLOWED_RESUME_EXTENSIONS)),
        "allowed_jd_extensions": sorted(list(ALLOWED_JD_EXTENSIONS)),
        "scoring_weights_default": {
            "skill_match": 0.40,
            "text_baseline": 0.20,
            "semantic_match": 0.40
        }
    }


@app.post("/api/analyze")
async def analyze_documents(
    resume_file: UploadFile = File(..., description="Candidate resume (PDF, DOCX, TXT)"),
    jd_text: Optional[str] = Form(None, description="Pasted Job Description text"),
    jd_file: Optional[UploadFile] = File(None, description="Job Description document (PDF, DOCX, TXT)"),
    preferred_method: str = Form("auto", description="'auto', 'semantic', or 'classical'")
):
    """
    Analyzes a candidate resume against a job description.
    Enforces upload constraints, extracts structured skills, computes similarity,
    and returns a full compatibility breakdown.
    """
    # 1. Validate inputs
    if not resume_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file is required."
        )

    has_jd_text = bool(jd_text and jd_text.strip())
    has_jd_file = bool(jd_file and jd_file.filename)

    if not has_jd_text and not has_jd_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required. Please paste JD text or upload a JD document."
        )

    # 2. Read resume into memory with bounded size checking
    try:
        resume_bytes = await resume_file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded resume file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading uploaded resume: {str(e)}"
        )

    if len(resume_bytes) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Resume file exceeds the 25 MB limit (received {len(resume_bytes)/(1024*1024):.2f} MB)."
        )

    # 3. Read JD file if provided
    jd_bytes = None
    jd_filename = None
    if has_jd_file:
        try:
            jd_bytes = await jd_file.read()
            jd_filename = jd_file.filename
        except Exception as e:
            logger.error(f"Failed to read uploaded JD file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading uploaded job description document: {str(e)}"
            )

        if len(jd_bytes) > MAX_JD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Job description file exceeds the 10 MB limit (received {len(jd_bytes)/(1024*1024):.2f} MB)."
            )

    # 4. Execute Unified ML Pipeline
    try:
        logger.info(f"Processing candidate analysis for resume='{resume_file.filename}' (method={preferred_method})")
        result = analyze_candidate(
            resume_input=resume_bytes,
            resume_filename=resume_file.filename,
            jd_input=jd_bytes if has_jd_file else jd_text,
            jd_filename=jd_filename,
            preferred_method=preferred_method
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except FileSizeExceededError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=e.message)
    except PageLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except TextLengthExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=e.message)
    except (EncryptedDocumentError, CorruptedDocumentError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except EmptyDocumentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception(f"Unexpected error during candidate analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal processing error during analysis: {str(e)}"
        )


@app.post("/api/export/pdf")
async def export_pdf_report(analysis_result: Dict[str, Any]):
    """
    Generates and downloads a publication-quality PDF report from the analysis result.
    """
    if not analysis_result or "overall_score" not in analysis_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis result payload provided."
        )

    try:
        pdf_bytes = generate_pdf_report(analysis_result)
        req_id = analysis_result.get("request_id", "report")[:8]
        filename = f"TalentLens_Report_{req_id}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            }
        )
    except Exception as e:
        logger.exception(f"Failed to generate PDF report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
