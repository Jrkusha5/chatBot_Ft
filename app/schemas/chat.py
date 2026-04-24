from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)
    source_id: str | None = None


class Citation(BaseModel):
    source_id: str | None = None
    source_name: str | None = None
    source_type: str | None = None
    chunk_id: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    confidence: float
    citations: list[Citation]
