from app.services.retrieval.retriever import RetrievedChunk


def build_rag_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context_lines: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        src = chunk.metadata.get("source_name", "unknown")
        context_lines.append(f"[{idx}] source={src} chunk_id={chunk.chunk_id}\n{chunk.content}")

    context = "\n\n".join(context_lines) if context_lines else "No context provided."
    return (
        "You are a helpful assistant. Answer using only the provided context. "
        "If the context is insufficient, say you don't know.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}"
    )
