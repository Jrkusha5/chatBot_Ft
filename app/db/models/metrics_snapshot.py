from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MetricsSnapshot(Base):
    __tablename__ = "metrics_snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    total_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    chat_requests: Mapped[int] = mapped_column(Integer, default=0)
    ingest_requests: Mapped[int] = mapped_column(Integer, default=0)
    feedback_submissions: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
