from io import BytesIO
from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class TextSegment:
    text: str
    page: int | None = None
    section: str | None = None


def extract_text_from_file(filename: str, content: bytes) -> tuple[list[TextSegment], str]:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return _extract_pdf_segments(content), "pdf"
    if lowered.endswith(".md"):
        decoded = content.decode("utf-8", errors="ignore")
        return _extract_markdown_segments(decoded), "text"
    if lowered.endswith(".txt"):
        decoded = content.decode("utf-8", errors="ignore")
        return [TextSegment(text=decoded)], "text"
    raise ValueError("Unsupported file type. Supported: .pdf, .txt, .md")


def _extract_pdf_segments(content: bytes) -> list[TextSegment]:
    reader = PdfReader(BytesIO(content))
    segments: list[TextSegment] = []
    for index, page in enumerate(reader.pages, start=1):
        segments.append(TextSegment(text=page.extract_text() or "", page=index))
    return segments


def _extract_markdown_segments(content: str) -> list[TextSegment]:
    lines = content.splitlines()
    segments: list[TextSegment] = []
    section = "document"
    buffer: list[str] = []

    for line in lines:
        if line.lstrip().startswith("#"):
            if buffer:
                segments.append(TextSegment(text="\n".join(buffer), section=section))
                buffer = []
            section = line.lstrip("#").strip() or "untitled"
            continue
        buffer.append(line)

    if buffer:
        segments.append(TextSegment(text="\n".join(buffer), section=section))

    return segments or [TextSegment(text=content)]
