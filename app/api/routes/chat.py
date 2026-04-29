from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.chat_repo import ChatRepository
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services.rag.generator import generate_answer
from app.services.rag.prompt_builder import build_rag_prompt
from app.services.retrieval.retriever import Retriever
from app.services.telemetry.metrics import metrics_store

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    settings = get_settings()
    if len(payload.message) > settings.max_chat_message_chars:
        raise HTTPException(
            status_code=413,
            detail=f"message exceeds maximum length of {settings.max_chat_message_chars} characters",
        )

    chat_repo = ChatRepository(db)
    retriever = Retriever()

    try:
        chunks = retriever.retrieve(
            payload.message,
            top_k=payload.top_k,
            source_id=payload.source_id,
            source_filters=payload.source_filters,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    citations = [
        Citation(
            source_id=chunk.metadata.get("source_id"),
            source_name=chunk.metadata.get("source_name"),
            source_type=chunk.metadata.get("source_type"),
            page=chunk.metadata.get("page"),
            section=chunk.metadata.get("section"),
            chunk_id=chunk.chunk_id,
            score=chunk.score,
        )
        for chunk in chunks
    ]
    confidence = max((citation.score for citation in citations), default=0.0)

    has_context = bool(chunks) and confidence >= settings.confidence_threshold
    if not has_context:
        answer = "I don't know based on the available documents."
        citations = []
    else:
        prompt = build_rag_prompt(payload.message, chunks)
        try:
            answer = generate_answer(prompt)
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    session = chat_repo.get_or_create_session(payload.session_id)
    chat_repo.create_message(chat_session_id=session.id, role="user", content=payload.message)
    chat_repo.create_message(
        chat_session_id=session.id,
        role="assistant",
        content=answer,
        confidence=confidence,
    )
    metrics_store.observe_chat_request()

    return ChatResponse(
        session_id=session.id,
        answer=answer,
        confidence=confidence,
        citations=citations,
    )
