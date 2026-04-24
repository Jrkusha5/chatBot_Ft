from app.db.models.source import Source


def test_list_and_delete_sources(client, db_session, monkeypatch):
    source = Source(
        id="source-1",
        source_type="pdf",
        name="doc.pdf",
        location="upload://doc.pdf",
        content_hash="abc",
        chunks_indexed=2,
    )
    db_session.add(source)
    db_session.commit()

    list_response = client.get("/sources")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    from app.api.routes import sources as sources_route

    class FakeCollection:
        def delete(self, where):
            assert where == {"source_id": "source-1"}

    monkeypatch.setattr(sources_route, "ensure_default_collection", lambda: FakeCollection())

    delete_response = client.delete("/sources/source-1")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
