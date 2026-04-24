from datetime import datetime

from pydantic import BaseModel


class SourceResponse(BaseModel):
    id: str
    source_type: str
    name: str
    location: str
    chunks_indexed: int
    created_at: datetime


class SourceDeleteResponse(BaseModel):
    source_id: str
    status: str
