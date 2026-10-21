"""
parser.py

Robust document extraction module supporting PDF, DOCX, and TXT files.
Enforces size limits, page counts, text limits, encryption checks, and format validation.
"""

import io
import os
from typing import Tuple, Dict, Any, Union
import pypdf
import docx

from .limits import (
    MAX_RESUME_SIZE_BYTES,
    MAX_JD_SIZE_BYTES,
    MAX_PDF_PAGES,
    MAX_EXTRACTED_TEXT_BYTES,
    FileSizeExceededError,
    PageLimitExceededError,
    TextLengthExceededError,
    UnsupportedFormatError,
    CorruptedDocumentError,
    EncryptedDocumentError,
    EmptyDocumentError,
)


def validate_file_size(file_bytes: bytes, max_bytes: int, file_label: str = "File") -> None:
    """Validate that the file byte length does not exceed maximum allowed."""
    actual_size = len(file_bytes)
    if actual_size > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        actual_mb = actual_size / (1024 * 1024)
        raise FileSizeExceededError(
            f"{file_label} exceeds configured size limit of {max_mb:.1f} MB (uploaded size: {actual_mb:.2f} MB)."
        )
    if actual_size == 0:
        raise EmptyDocumentError(f"{file_label} is completely empty (0 bytes).")


def detect_format_and_validate(filename: str, file_bytes: bytes) -> str:
    """
    Validate file extension and header signature (magic bytes).
    Returns normalized format: 'pdf', 'docx', or 'txt'.
    """
    ext = os.path.splitext(filename.lower())[1]
    if ext not in {".pdf", ".docx", ".txt"}:
        raise UnsupportedFormatError(
            f"Unsupported file extension '{ext}'. Only .pdf, .docx, and .txt files are supported."
        )

    # Magic byte verification
    if ext == ".pdf":
        if not file_bytes.startswith(b"%PDF"):
            raise CorruptedDocumentError("Invalid PDF file: Missing %PDF signature.")
        return "pdf"

    if ext == ".docx":
        # DOCX is a zip archive (starts with PK\x03\x04 or PK\x05\x06)
        if not (file_bytes.startswith(b"PK\x03\x04") or file_bytes.startswith(b"PK\x05\x06")):
            raise CorruptedDocumentError("Invalid DOCX file: Not a valid OpenXML ZIP package.")
        return "docx"

    # For .txt, verify it is text and does not contain predominantly null bytes
    if b"\x00" in file_bytes[:1024]:
        raise CorruptedDocumentError("Invalid TXT file: Binary content detected.")
    return "txt"


def extract_text_from_pdf(stream: io.BytesIO) -> Tuple[str, int]:
    """
    Extract text from PDF stream with page limit and encryption checking.
    Returns (extracted_text, page_count).
    """
    try:
        reader = pypdf.PdfReader(stream)
    except Exception as e:
        raise CorruptedDocumentError(f"Failed to parse PDF document: {str(e)}")

    if reader.is_encrypted:
        try:
            # Try decrypting with empty password if possible
            decrypted = reader.decrypt("")
            if decrypted == 0:
                raise EncryptedDocumentError("PDF is encrypted and cannot be opened without a password.")
        except Exception:
            raise EncryptedDocumentError("PDF is encrypted and password protected.")

    num_pages = len(reader.pages)
    if num_pages > MAX_PDF_PAGES:
        raise PageLimitExceededError(
            f"PDF exceeds the maximum allowed page limit of {MAX_PDF_PAGES} pages (found {num_pages} pages)."
        )

    extracted_pages = []
    total_bytes = 0

    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
        except Exception as e:
            # Handle page rendering issue
            page_text = ""

        page_utf8_len = len(page_text.encode("utf-8", errors="replace"))
        total_bytes += page_utf8_len

        if total_bytes > MAX_EXTRACTED_TEXT_BYTES:
            raise TextLengthExceededError(
                f"Extracted document text exceeds the maximum limit of {MAX_EXTRACTED_TEXT_BYTES // (1024*1024)} MB."
            )

        extracted_pages.append(page_text)

    full_text = "\n\n".join(extracted_pages).strip()
    return full_text, num_pages


def extract_text_from_docx(stream: io.BytesIO) -> Tuple[str, int]:
    """
    Extract text from DOCX stream (paragraphs + tables).
    Returns (extracted_text, paragraph_count).
    """
    try:
        doc = docx.Document(stream)
    except Exception as e:
        raise CorruptedDocumentError(f"Failed to parse DOCX document: {str(e)}")

    parts = []
    total_bytes = 0

    # Extract paragraphs
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            parts.append(txt)
            total_bytes += len(txt.encode("utf-8", errors="replace"))
            if total_bytes > MAX_EXTRACTED_TEXT_BYTES:
                raise TextLengthExceededError(
                    f"Extracted DOCX text exceeds maximum limit of {MAX_EXTRACTED_TEXT_BYTES // (1024*1024)} MB."
                )

    # Extract tables
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                row_txt = " | ".join(row_cells)
                parts.append(row_txt)
                total_bytes += len(row_txt.encode("utf-8", errors="replace"))
                if total_bytes > MAX_EXTRACTED_TEXT_BYTES:
                    raise TextLengthExceededError(
                        f"Extracted DOCX text exceeds maximum limit of {MAX_EXTRACTED_TEXT_BYTES // (1024*1024)} MB."
                    )

    full_text = "\n".join(parts).strip()
    return full_text, len(parts)


def extract_text_from_txt(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from TXT bytes, testing UTF-8 and fallback encodings.
    Returns (extracted_text, line_count).
    """
    if len(file_bytes) > MAX_EXTRACTED_TEXT_BYTES:
        raise TextLengthExceededError(
            f"Extracted TXT file exceeds the maximum limit of {MAX_EXTRACTED_TEXT_BYTES // (1024*1024)} MB."
        )

    # Decode
    text = None
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        raise CorruptedDocumentError("Unable to decode TXT file with standard text encodings.")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    full_text = "\n".join(lines).strip()
    return full_text, len(lines)


def extract_document_text(
    file_input: Union[bytes, str],
    filename: str,
    is_resume: bool = True
) -> Tuple[str, Dict[str, Any]]:
    """
    Main extraction interface. Accepts either file bytes or a file path on disk.
    
    Args:
        file_input: Raw bytes of the file, or path to file on disk.
        filename: Name of the file (used for extension detection and error logging).
        is_resume: Whether this is a resume (25MB limit) or a JD (10MB limit).
        
    Returns:
        (extracted_text, metadata_dict)
    """
    max_size = MAX_RESUME_SIZE_BYTES if is_resume else MAX_JD_SIZE_BYTES
    label = "Resume document" if is_resume else "Job description document"

    if isinstance(file_input, str):
        if not os.path.exists(file_input):
            raise DocumentParserError(f"File not found on disk: {file_input}")
        with open(file_input, "rb") as f:
            file_bytes = f.read()
    else:
        file_bytes = file_input

    # 1. Enforce file size limit
    validate_file_size(file_bytes, max_size, label)

    # 2. Validate format & magic signature
    fmt = detect_format_and_validate(filename, file_bytes)

    stream = io.BytesIO(file_bytes)
    page_or_unit_count = 1

    # 3. Extract text
    if fmt == "pdf":
        raw_text, page_or_unit_count = extract_text_from_pdf(stream)
    elif fmt == "docx":
        raw_text, page_or_unit_count = extract_text_from_docx(stream)
    elif fmt == "txt":
        raw_text, page_or_unit_count = extract_text_from_txt(file_bytes)
    else:
        raise UnsupportedFormatError(f"Unsupported format: {fmt}")

    # 4. Check for non-empty extracted text
    if not raw_text or not raw_text.strip():
        raise EmptyDocumentError(
            f"{label} ('{filename}') contains no readable text. If this is a scanned image, please provide a text-based document."
        )

    # 5. Build metadata
    text_utf8_bytes = len(raw_text.encode("utf-8", errors="replace"))
    word_count = len(raw_text.split())

    metadata = {
        "filename": os.path.basename(filename),
        "format": fmt,
        "file_size_bytes": len(file_bytes),
        "extracted_text_bytes": text_utf8_bytes,
        "word_count": word_count,
        "char_count": len(raw_text),
        "unit_count": page_or_unit_count,  # pages for PDF, blocks/lines for DOCX/TXT
        "is_resume": is_resume,
    }

    return raw_text, metadata
