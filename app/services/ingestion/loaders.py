from io import BytesIO

from pypdf import PdfReader


def extract_text_from_file(filename: str, content: bytes) -> tuple[str, str]:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return _extract_pdf_text(content), "pdf"
    if lowered.endswith(".txt") or lowered.endswith(".md"):
        return content.decode("utf-8", errors="ignore"), "text"
    raise ValueError("Unsupported file type. Supported: .pdf, .txt, .md")


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)
