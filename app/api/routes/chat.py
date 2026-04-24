from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
    chat_repo = ChatRepository(db)
    retriever = Retriever()

    try:
        chunks = retriever.retrieve(
            payload.message,
            top_k=payload.top_k,
            source_id=payload.source_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    citations = [
        Citation(
            source_id=chunk.metadata.get("source_id"),
            source_name=chunk.metadata.get("source_name"),
            source_type=chunk.metadata.get("source_type"),
            chunk_id=chunk.chunk_id,
            score=chunk.score,
        )
        for chunk in chunks
    ]
    confidence = max((citation.score for citation in citations), default=0.0)

    if not chunks:
        answer = "I don't know based on the available documents."
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
    metrics_store.chat_requests += 1

    return ChatResponse(
        session_id=session.id,
        answer=answer,
        confidence=confidence,
        citations=citations,
    )
