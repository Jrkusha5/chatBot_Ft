from app.vectorstore.collection_manager import ensure_default_collection


def index_chunks(
    *,
    source_id: str,
    source_name: str,
    source_type: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    collection = ensure_default_collection()
    ids = [f"{source_id}:{idx}" for idx in range(len(chunks))]
    metadatas = [
        {
            "source_id": source_id,
            "source_name": source_name,
            "source_type": source_type,
            "chunk_index": idx,
        }
        for idx in range(len(chunks))
    ]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)
