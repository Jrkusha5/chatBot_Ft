from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    chat_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True
    )
    source_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    message_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("messages.id"), nullable=True)
    rating: Mapped[str] = mapped_column(String(20))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source = relationship("Source", back_populates="feedback_items")
