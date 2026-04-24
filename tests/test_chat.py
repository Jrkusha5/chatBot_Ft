from app.services.retrieval.retriever import RetrievedChunk


def test_chat_returns_answer_with_citations(client, monkeypatch):
    from app.api.routes import chat as chat_route

    def fake_retrieve(self, query, top_k=None, source_id=None):
        return [
            RetrievedChunk(
                chunk_id="src-1:0",
                content="FastAPI is a web framework.",
                score=0.91,
                metadata={"source_id": "src-1", "source_name": "doc1.pdf", "source_type": "pdf"},
            )
        ]

    monkeypatch.setattr(chat_route.Retriever, "retrieve", fake_retrieve)
    monkeypatch.setattr(chat_route, "generate_answer", lambda prompt: "FastAPI is a Python web framework.")

    response = client.post(
        "/chat",
        json={"session_id": "session-1", "message": "What is FastAPI?", "top_k": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "session-1"
    assert "FastAPI" in data["answer"]
    assert len(data["citations"]) == 1
    assert data["citations"][0]["source_name"] == "doc1.pdf"
