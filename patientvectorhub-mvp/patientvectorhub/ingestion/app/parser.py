"""
Document parsing. MVP supports plain text and PDF. Scanned/image-only PDFs
will yield empty text - OCR is explicitly out of scope for the MVP (see
README "Phase 2 / known gaps").
"""
import os
from pypdf import PdfReader


def parse_document(storage_path: str) -> str:
    ext = os.path.splitext(storage_path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(storage_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    if ext in (".txt", ".md"):
        with open(storage_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    raise ValueError(f"Unsupported file type: {ext}. MVP supports .pdf, .txt, .md")
