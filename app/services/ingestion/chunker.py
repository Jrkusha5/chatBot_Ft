from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class ChunkPayload:
    content: str
    page: int | None = None
    section: str | None = None


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap
    if not text:
        return []

    chunks: list[str] = []
    step = max(1, chunk_size - chunk_overlap)
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
    return chunks


def chunk_text_with_metadata(
    text: str,
    *,
    page: int | None = None,
    section: str | None = None,
) -> list[ChunkPayload]:
    return [
        ChunkPayload(content=chunk, page=page, section=section)
        for chunk in chunk_text(text)
    ]
