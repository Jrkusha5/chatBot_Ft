import logging

from fastapi import FastAPI
from fastapi import Request
from starlette.responses import JSONResponse

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

logger = logging.getLogger(__name__)
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
async def limit_json_request_size(request: Request, call_next):
    """Reject oversized JSON bodies early (does not apply to multipart /ingest)."""
    if request.method not in ("POST", "PUT", "PATCH"):
        return await call_next(request)
    path = request.url.path
    if path.startswith("/ingest"):
        return await call_next(request)
    cfg = get_settings()
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            size = int(content_length)
        except ValueError:
            return await call_next(request)
        if size > cfg.max_json_body_bytes:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"Request body exceeds maximum size of {cfg.max_json_body_bytes} bytes",
                },
            )
    return await call_next(request)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = now_ms()
    response = await call_next(request)
    duration = now_ms() - start
    metrics_store.observe_request(latency_ms=duration, is_error=response.status_code >= 400)
    return response


@app.on_event("startup")
def on_startup() -> None:
    cfg = get_settings()
    if cfg.app_env.lower() == "production":
        logger.warning(
            "APP_ENV=production: configure GEMINI_API_KEY, DATABASE_URL, and other secrets via your "
            "hosting provider (environment or secret manager). Do not rely on a committed .env file."
        )
    init_db()
    ensure_default_collection()
