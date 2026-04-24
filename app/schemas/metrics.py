from pydantic import BaseModel


class MetricsResponse(BaseModel):
    request_count: int
    error_count: int
    avg_latency_ms: float
    chat_requests: int
    ingest_requests: int
    feedback_submissions: int
