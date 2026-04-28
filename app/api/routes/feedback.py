from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.feedback_repo import FeedbackRepository
from app.schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from app.services.telemetry.metrics import metrics_store

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def create_feedback(payload: FeedbackCreateRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    repo = FeedbackRepository(db)
    feedback = repo.create_feedback(
        chat_session_id=payload.chat_session_id,
        rating=payload.rating,
        comment=payload.comment,
        source_id=payload.source_id,
        message_id=payload.message_id,
    )
    metrics_store.observe_feedback_submission()
    return FeedbackResponse(
        id=feedback.id,
        chat_session_id=feedback.chat_session_id,
        rating=feedback.rating,
        comment=feedback.comment,
        source_id=feedback.source_id,
        message_id=feedback.message_id,
        created_at=feedback.created_at,
    )
