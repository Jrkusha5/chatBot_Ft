from fastapi import APIRouter

from app.schemas.metrics import MetricsResponse
from app.services.telemetry.metrics import metrics_store

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    return MetricsResponse(**metrics_store.snapshot())
