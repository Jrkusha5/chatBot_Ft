from app.db.models.chat_session import ChatSession


def test_feedback_and_metrics(client, db_session):
    session = ChatSession(id="session-feedback")
    db_session.add(session)
    db_session.commit()

    feedback_response = client.post(
        "/feedback",
        json={
            "chat_session_id": "session-feedback",
            "rating": "up",
            "comment": "Helpful response",
        },
    )
    assert feedback_response.status_code == 200
    payload = feedback_response.json()
    assert payload["rating"] == "up"

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    assert metrics["request_count"] >= 2
    assert metrics["feedback_submissions"] >= 1
