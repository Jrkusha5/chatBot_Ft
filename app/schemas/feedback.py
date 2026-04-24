from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    chat_session_id: str
    rating: str = Field(pattern="^(up|down)$")
    comment: str | None = None
    source_id: str | None = None
    message_id: str | None = None


class FeedbackResponse(BaseModel):
    id: str
    chat_session_id: str
    rating: str
    comment: str | None = None
    source_id: str | None = None
    message_id: str | None = None
    created_at: datetime
