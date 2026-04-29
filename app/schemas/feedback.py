from datetime import datetime

from pydantic import BaseModel, Field

from app.core.limits import FEEDBACK_COMMENT_HARD_MAX, SESSION_ID_HARD_MAX


class FeedbackCreateRequest(BaseModel):
    chat_session_id: str = Field(min_length=1, max_length=SESSION_ID_HARD_MAX)
    rating: str = Field(pattern="^(up|down)$")
    comment: str | None = Field(default=None, max_length=FEEDBACK_COMMENT_HARD_MAX)
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
