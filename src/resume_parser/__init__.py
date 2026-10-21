"""
src/resume_parser

Document parsing package supporting PDF, DOCX, and TXT formats with
robust boundary limits and validation.
"""

from .limits import (
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

from .parser import (
    extract_document_text,
    detect_format_and_validate,
    validate_file_size,
)

__all__ = [
    "MAX_RESUME_SIZE_BYTES",
    "MAX_JD_SIZE_BYTES",
    "MAX_PDF_PAGES",
    "MAX_EXTRACTED_TEXT_BYTES",
    "PROCESSING_TIMEOUT_SECONDS",
    "ALLOWED_RESUME_EXTENSIONS",
    "ALLOWED_JD_EXTENSIONS",
    "DocumentParserError",
    "FileSizeExceededError",
    "PageLimitExceededError",
    "TextLengthExceededError",
    "UnsupportedFormatError",
    "CorruptedDocumentError",
    "EncryptedDocumentError",
    "EmptyDocumentError",
    "extract_document_text",
    "detect_format_and_validate",
    "validate_file_size",
]
