from app.core.config import get_settings
from app.services.gemini_client import get_gemini_client


def embed_texts(texts: list[str], *, for_query: bool = False) -> list[list[float]]:
    if not texts:
        return []

    settings = get_settings()
    client = get_gemini_client()
    task_type = "RETRIEVAL_QUERY" if for_query else "RETRIEVAL_DOCUMENT"

    all_vectors: list[list[float]] = []
    batch_size = 100

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.models.embed_content(
            model=settings.embedding_model,
            contents=batch,
            config={"task_type": task_type},
        )
        if not response.embeddings or len(response.embeddings) != len(batch):
            raise ValueError("Embedding request failed or returned unexpected number of vectors")

        for item in response.embeddings:
            values = item.values
            if not values:
                raise ValueError("Empty embedding vector from Gemini")
            all_vectors.append(list(values))

    return all_vectors
