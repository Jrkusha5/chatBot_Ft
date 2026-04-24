def test_ingest_file_indexes_chunks(client, monkeypatch):
    from app.api.routes import ingest as ingest_route

    monkeypatch.setattr(
        ingest_route,
        "extract_text_from_file",
        lambda filename, content: ("This is a test document for ingestion.", "text"),
    )
    monkeypatch.setattr(ingest_route, "embed_texts", lambda chunks: [[0.1, 0.2] for _ in chunks])
    monkeypatch.setattr(ingest_route, "index_chunks", lambda **kwargs: len(kwargs["chunks"]))

    files = {"file": ("sample.txt", b"dummy content", "text/plain")}
    response = client.post("/ingest/file", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "indexed"
    assert data["chunks_indexed"] >= 1
