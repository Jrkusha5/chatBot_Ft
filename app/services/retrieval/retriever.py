from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings
from app.services.ingestion.embedder import embed_texts
from app.vectorstore.collection_manager import ensure_default_collection


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    metadata: dict[str, Any]


class Retriever:
    def __init__(self) -> None:
        self.settings = get_settings()

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        source_id: str | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        query_embedding = embed_texts([query])[0]
        collection = ensure_default_collection()
        limit = top_k or self.settings.top_k

        where_filter = {"source_id": source_id} if source_id else None
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
        return _normalize_query_results(results)


def _normalize_query_results(results: dict[str, Any]) -> list[RetrievedChunk]:
    ids = results.get("ids", [[]])[0] or []
    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    chunks: list[RetrievedChunk] = []
    for index, chunk_id in enumerate(ids):
        content = documents[index] if index < len(documents) else ""
        metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
        distance = distances[index] if index < len(distances) else 1.0
        score = max(0.0, 1.0 - float(distance))
        chunks.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                content=content,
                metadata=metadata,
                score=score,
            )
        )
    return chunks
