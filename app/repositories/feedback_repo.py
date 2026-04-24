from sqlalchemy.orm import Session

from app.db.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_feedback(
        self,
        *,
        chat_session_id: str,
        rating: str,
        comment: str | None = None,
        source_id: str | None = None,
        message_id: str | None = None,
    ) -> Feedback:
        feedback = Feedback(
            chat_session_id=chat_session_id,
            rating=rating,
            comment=comment,
            source_id=source_id,
            message_id=message_id,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
