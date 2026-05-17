from io import BytesIO
from pathlib import Path
from typing import List

from docx import Document
from pypdf import PdfReader


def validate_file_size(file_bytes: bytes, max_upload_mb: int) -> None:
    if len(file_bytes) > max_upload_mb * 1024 * 1024:
        raise ValueError(f"File is too large. Maximum allowed size is {max_upload_mb} MB.")


def extract_text_from_bytes(file_name: str, file_bytes: bytes, max_upload_mb: int) -> str:
    validate_file_size(file_bytes, max_upload_mb)
    suffix = Path(file_name).suffix.lower()

    if suffix == ".pdf":
        pages: List[str] = []
        reader = PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        content = "\n".join(pages).strip()
    elif suffix == ".docx":
        document = Document(BytesIO(file_bytes))
        content = "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
    elif suffix == ".txt":
        content = ""
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                content = file_bytes.decode(encoding).strip()
                break
            except UnicodeDecodeError:
                continue
        if not content:
            content = file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")

    if not content:
        raise ValueError("The uploaded file does not contain readable text.")
    return content
