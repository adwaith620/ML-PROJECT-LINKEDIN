"""
test_resume_parser.py

Comprehensive tests for document parsing, format detection, and limit enforcement.
"""

import io
import unittest
import pypdf
import docx

from src.resume_parser import (
    extract_document_text,
    detect_format_and_validate,
    validate_file_size,
    MAX_RESUME_SIZE_BYTES,
    MAX_JD_SIZE_BYTES,
    MAX_PDF_PAGES,
    MAX_EXTRACTED_TEXT_BYTES,
    FileSizeExceededError,
    PageLimitExceededError,
    TextLengthExceededError,
    UnsupportedFormatError,
    CorruptedDocumentError,
    EmptyDocumentError,
)


def create_synthetic_pdf(page_count: int = 1, text_per_page: str = "Test resume text") -> bytes:
    """Generates an in-memory PDF using pypdf writer."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=612, height=792)
    
    # Write to buffer
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def create_synthetic_pdf_with_text(text: str) -> bytes:
    """Generates a PDF with actual extractable text using reportlab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    return buf.getvalue()


def create_synthetic_docx(text: str) -> bytes:
    """Generates an in-memory DOCX document."""
    doc = docx.Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class TestResumeParser(unittest.TestCase):

    def test_valid_txt_extraction(self):
        txt_content = b"Candidate Name\nExperienced Python developer with React and SQL."
        text, meta = extract_document_text(txt_content, "resume.txt", is_resume=True)
        self.assertEqual(meta["format"], "txt")
        self.assertIn("Python developer", text)
        self.assertGreater(meta["word_count"], 0)

    def test_valid_docx_extraction(self):
        docx_bytes = create_synthetic_docx("Senior Software Engineer with Docker and Kubernetes experience.")
        text, meta = extract_document_text(docx_bytes, "candidate.docx", is_resume=True)
        self.assertEqual(meta["format"], "docx")
        self.assertIn("Docker", text)
        self.assertIn("Kubernetes", text)

    def test_valid_pdf_extraction(self):
        pdf_bytes = create_synthetic_pdf_with_text("Machine Learning Engineer skilled in PyTorch and NLP.")
        text, meta = extract_document_text(pdf_bytes, "resume.pdf", is_resume=True)
        self.assertEqual(meta["format"], "pdf")
        self.assertIn("Machine Learning", text)
        self.assertIn("PyTorch", text)

    def test_empty_file_rejection(self):
        with self.assertRaises(EmptyDocumentError):
            extract_document_text(b"", "empty.txt", is_resume=True)

    def test_unsupported_format_rejection(self):
        with self.assertRaises(UnsupportedFormatError):
            extract_document_text(b"some content", "resume.exe", is_resume=True)

    def test_corrupted_pdf_rejection(self):
        corrupted_bytes = b"Not a valid PDF header content"
        with self.assertRaises(CorruptedDocumentError):
            extract_document_text(corrupted_bytes, "fake.pdf", is_resume=True)

    def test_corrupted_docx_rejection(self):
        corrupted_bytes = b"PK\x03\x04butNotValidZipDataAtAll"
        with self.assertRaises(CorruptedDocumentError):
            extract_document_text(corrupted_bytes, "fake.docx", is_resume=True)

    def test_resume_size_limit_exceeded(self):
        oversized_bytes = b"A" * (MAX_RESUME_SIZE_BYTES + 1024)
        with self.assertRaises(FileSizeExceededError):
            validate_file_size(oversized_bytes, MAX_RESUME_SIZE_BYTES, "Resume")

    def test_jd_size_limit_exceeded(self):
        oversized_bytes = b"A" * (MAX_JD_SIZE_BYTES + 1024)
        with self.assertRaises(FileSizeExceededError):
            validate_file_size(oversized_bytes, MAX_JD_SIZE_BYTES, "Job Description")

    def test_pdf_page_limit_exceeded(self):
        # Create a PDF with 105 pages (exceeding 100 page limit)
        pdf_105_pages = create_synthetic_pdf(page_count=105)
        with self.assertRaises(PageLimitExceededError):
            extract_document_text(pdf_105_pages, "long_resume.pdf", is_resume=True)


if __name__ == "__main__":
    unittest.main()
