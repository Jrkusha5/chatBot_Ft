from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.chat import router as chat_router
from app.api.routes.sources import router as sources_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.vectorstore.collection_manager import ensure_default_collection

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, debug=settings.app_debug)
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(chat_router)
app.include_router(sources_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    ensure_default_collection()
