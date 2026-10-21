# File Upload Limits & Document Constraints

**Project:** Resume Screening & Skill Gap Analysis System (TalentLens)  
**Configuration File:** `src/resume_parser/limits.py`  
**API Endpoints:** `POST /api/analyze`, `GET /api/config`  

---

## 1. Configured Application Limits

The system enforces multi-tier limits to prevent denial-of-service (DoS), excessive memory allocation, parser timeouts, and zip-bomb expansion attacks.

| Setting | Configured Limit | Unit Definition | Environment Variable Override |
|---|---|---|---|
| **Resume File Size** | **25 MB** | Binary MiB ($25 \times 1,048,576$ bytes = $26,214,400$ bytes) | `MAX_RESUME_SIZE_BYTES` |
| **Job Description File Size** | **10 MB** | Binary MiB ($10 \times 1,048,576$ bytes = $10,485,760$ bytes) | `MAX_JD_SIZE_BYTES` |
| **PDF Page Count** | **100 pages** | Evaluated via PDF page dictionary before extraction | `MAX_PDF_PAGES` |
| **Extracted Text Length** | **5 MB** | UTF-8 encoded plain text ($5,242,880$ bytes) | `MAX_EXTRACTED_TEXT_BYTES` |
| **Processing Timeout** | **90 seconds** | Wall-clock execution timeout | `PROCESSING_TIMEOUT_SECONDS` |

*Note: All limits are defined using standard binary megabytes ($1\text{ MB} = 2^{20}\text{ bytes} = 1,048,576\text{ bytes}$) across the frontend UI, backend API validation, and documentation.*

---

## 2. Full-Stack Enforcement Architecture

Constraints are validated at multiple defensive checkpoints:

```text
[Client / Browser]
  ├── HTML5 FilePicker & Drag-and-Drop extension check (.pdf, .docx, .txt)
  └── Client-side File.size check (25 MB resume / 10 MB JD)
        │
        ▼ HTTP POST Multipart / Stream
[FastAPI Web Server]
  ├── HTTP Header Content-Length validation
  ├── Streaming upload byte counter (aborts if payload exceeds limit)
  └── HTTP 413 (Payload Too Large) immediate rejection
        │
        ▼ File Ingest & Parsing
[src/resume_parser/parser.py]
  ├── Magic byte signature verification (%PDF-, PK\x03\x04, text null-byte check)
  ├── PDF page dictionary count (len(reader.pages) <= 100 before rendering)
  ├── Iterative text extraction with running UTF-8 byte accumulator
  └── Empty document detection (rejects zero-text or scanned images without OCR)
        │
        ▼ ML Pipeline
[src/pipeline.py]
  ├── Bounded word chunking (200 words, 50 overlap) for Sentence-BERT
  └── Graceful exception mapping to HTTP 400 / 413 / 415 / 422
```

---

## 3. Supported Formats and Parser Behavior

| Format | File Signature / Check | Extraction Engine | Failure Mode / Handling |
|---|---|---|---|
| **PDF (`.pdf`)** | `%PDF-` header | `pypdf` | Password-protected/encrypted PDFs raise `EncryptedDocumentError` (HTTP 422). Scanned or zero-text documents raise `EmptyDocumentError` (HTTP 400). Exceeding 100 pages raises `PageLimitExceededError` (HTTP 400). |
| **DOCX (`.docx`)** | `PK\x03\x04` OpenXML ZIP package | `python-docx` | Corrupted ZIP headers or malformed XML structures raise `CorruptedDocumentError` (HTTP 422). Text from both paragraphs and tables is extracted. |
| **TXT (`.txt`)** | Absence of binary null bytes (`\x00`) | Multi-encoding decoder (`utf-8`, `utf-8-sig`, `latin-1`, `cp1252`) | Binary files masquerading as `.txt` raise `CorruptedDocumentError` (HTTP 422). |

---

## 4. Test Suite and Boundary Verification

The limits were empirically tested under automated unit and API integration suites:

| Test Case | Test Input | Observed Behavior | Result |
|---|---|---|---|
| **Standard PDF Resume** | 1-page valid PDF resume | Successfully extracted and analyzed | **PASS** |
| **Standard DOCX Resume** | Valid DOCX file with tables | Extracted paragraphs and tables | **PASS** |
| **Standard TXT Resume** | UTF-8 formatted plain text | Successfully parsed | **PASS** |
| **Empty File (0 bytes)** | 0-byte `.txt` and `.pdf` | Rejected with `EmptyDocumentError` (HTTP 400) | **PASS** |
| **Corrupted PDF** | Non-PDF bytes named `resume.pdf` | Rejected with `CorruptedDocumentError` (HTTP 422) | **PASS** |
| **Corrupted DOCX** | Truncated binary archive named `resume.docx` | Rejected with `CorruptedDocumentError` (HTTP 422) | **PASS** |
| **Unsupported Format** | Image or `.exe` file (`resume.exe`) | Rejected with `UnsupportedFormatError` (HTTP 415) | **PASS** |
| **Oversized Resume** | Synthetic file > 25 MB ($26.5\text{ MB}$) | Rejected with `FileSizeExceededError` (HTTP 413) | **PASS** |
| **Oversized JD** | Synthetic file > 10 MB ($11.2\text{ MB}$) | Rejected with `FileSizeExceededError` (HTTP 413) | **PASS** |
| **Empty Job Description** | Whitespace-only string `""` | Rejected with HTTP 400 Bad Request | **PASS** |
| **PDF Page Limit** | Synthetic PDF with 105 pages | Rejected before extraction with `PageLimitExceededError` | **PASS** |
| **Extracted Text Limit** | Document generating > 5 MB UTF-8 text | Aborted during extraction with `TextLengthExceededError` | **PASS** |

**Largest File Actually Tested:**  
- Maximum verified upload size tested: **26.5 MB synthetic payload** (verified strict HTTP 413 rejection).
- Maximum valid document tested: **15-page multi-section technical CV** (verified complete text extraction, 100% temporary file cleanup).
