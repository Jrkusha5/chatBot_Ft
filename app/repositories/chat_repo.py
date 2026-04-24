from sqlalchemy.orm import Session

from app.db.models.chat_session import ChatSession
from app.db.models.message import Message


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create_session(self, session_id: str) -> ChatSession:
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            return session
        session = ChatSession(id=session_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def create_message(
        self,
        *,
        chat_session_id: str,
        role: str,
        content: str,
        confidence: float | None = None,
    ) -> Message:
        message = Message(
            chat_session_id=chat_session_id,
            role=role,
            content=content,
            confidence=confidence,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
