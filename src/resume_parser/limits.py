"""
limits.py

Central configuration and exception definitions for file upload limits,
document sizes, page constraints, and text lengths.
"""

import os

# Configurable Limits (defaults in binary MiB as standard in filesystems / HTTP specs)
# Can be overridden via environment variables if desired.
MAX_RESUME_SIZE_BYTES: int = int(os.getenv("MAX_RESUME_SIZE_BYTES", 25 * 1024 * 1024))  # 25 MB
MAX_JD_SIZE_BYTES: int = int(os.getenv("MAX_JD_SIZE_BYTES", 10 * 1024 * 1024))          # 10 MB
MAX_PDF_PAGES: int = int(os.getenv("MAX_PDF_PAGES", 100))                              # 100 pages
MAX_EXTRACTED_TEXT_BYTES: int = int(os.getenv("MAX_EXTRACTED_TEXT_BYTES", 5 * 1024 * 1024))  # 5 MB
PROCESSING_TIMEOUT_SECONDS: int = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", 90))       # 90 seconds

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_JD_EXTENSIONS = {".pdf", ".docx", ".txt"}


class DocumentParserError(Exception):
    """Base exception for all document parsing and validation issues."""
    def __init__(self, message: str, code: str = "PARSE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class FileSizeExceededError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="FILE_SIZE_EXCEEDED")


class PageLimitExceededError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="PAGE_LIMIT_EXCEEDED")


class TextLengthExceededError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="TEXT_LENGTH_EXCEEDED")


class UnsupportedFormatError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="UNSUPPORTED_FORMAT")


class CorruptedDocumentError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="CORRUPTED_DOCUMENT")


class EncryptedDocumentError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="ENCRYPTED_DOCUMENT")


class EmptyDocumentError(DocumentParserError):
    def __init__(self, message: str):
        super().__init__(message, code="EMPTY_DOCUMENT")
