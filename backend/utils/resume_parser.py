import os
import logging
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

MIN_USABLE_TEXT_LENGTH = 40


class ResumeExtractionError(Exception):
    """Raised when text cannot be reliably extracted from a resume file."""
    pass


def extract_text_from_pdf(file_stream):
    try:
        text_parts = []
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except ResumeExtractionError:
        raise
    except Exception as e:
        # pdfplumber/pdfminer can raise many different low-level exceptions
        # for corrupt, encrypted, or malformed PDFs (e.g. PDFSyntaxError,
        # PDFPasswordIncorrect). Normalize all of them to one clean error.
        logger.warning("Failed to parse PDF: %s", e)
        raise ResumeExtractionError("Could not read this PDF file.") from e


def extract_text_from_docx(file_stream):
    try:
        document = Document(file_stream)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except ResumeExtractionError:
        raise
    except Exception as e:
        # python-docx raises things like PackageNotFoundError (bad/renamed
        # zip) or plain KeyError/XML parse errors for a malformed .docx.
        logger.warning("Failed to parse DOCX: %s", e)
        raise ResumeExtractionError("Could not read this DOCX file.") from e


def get_extension(filename):
    return os.path.splitext(filename)[1].lower()


def extract_resume_text(file_storage):
    ext = get_extension(file_storage.filename)

    if ext == ".pdf":
        text = extract_text_from_pdf(file_storage.stream)
    elif ext == ".docx":
        text = extract_text_from_docx(file_storage.stream)
    else:
        raise ResumeExtractionError(f"Unsupported file extension: {ext}")

    if len(text) < MIN_USABLE_TEXT_LENGTH:
        raise ResumeExtractionError(
            "Extracted text is too short or empty — file may be a scanned "
            "image with no real text layer."
        )

    return text