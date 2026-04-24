from fastapi import FastAPI
from fastapi import Request

from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.chat import router as chat_router
from app.api.routes.sources import router as sources_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.metrics import router as metrics_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.services.telemetry.metrics import metrics_store, now_ms
from app.vectorstore.collection_manager import ensure_default_collection

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, debug=settings.app_debug)
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(chat_router)
app.include_router(sources_router)
app.include_router(feedback_router)
app.include_router(metrics_router)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = now_ms()
    response = await call_next(request)
    duration = now_ms() - start
    metrics_store.observe_request(latency_ms=duration, is_error=response.status_code >= 400)
    return response


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    ensure_default_collection()
