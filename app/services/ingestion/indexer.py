from typing import Any

from app.vectorstore.collection_manager import ensure_default_collection


def index_chunks(
    *,
    source_id: str,
    source_name: str,
    source_type: str,
    chunks: list[str],
    embeddings: list[list[float]],
    chunk_metadatas: list[dict[str, Any]] | None = None,
) -> int:
    collection = ensure_default_collection()
    ids = [f"{source_id}:{idx}" for idx in range(len(chunks))]
    metadatas: list[dict[str, Any]] = []
    for idx in range(len(chunks)):
        metadata: dict[str, Any] = {
            "source_id": source_id,
            "source_name": source_name,
            "source_type": source_type,
            "chunk_index": idx,
        }
        if chunk_metadatas and idx < len(chunk_metadatas):
            metadata.update(chunk_metadatas[idx])
        metadatas.append({key: value for key, value in metadata.items() if value is not None})

    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)
