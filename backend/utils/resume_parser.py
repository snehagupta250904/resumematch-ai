import os
from pypdf import PdfReader
from docx import Document

def parse_resume(file_path):
    """Extract plain text from a PDF or DOCX resume."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    text = text.strip()
    if not text:
        raise ValueError("No readable text found in resume")

    return text