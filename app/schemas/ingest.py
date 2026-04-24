from pydantic import BaseModel


class IngestResponse(BaseModel):
    source_id: str
    source_name: str
    source_type: str
    chunks_indexed: int
    status: str
