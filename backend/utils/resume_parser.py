import os
import pdfplumber
from docx import Document

MIN_USABLE_TEXT_LENGTH = 40


class ResumeExtractionError(Exception):
    """Raised when text cannot be reliably extracted from a resume file."""
    pass


def extract_text_from_pdf(file_stream):
    text_parts = []
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_stream):
    document = Document(file_stream)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


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