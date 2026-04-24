from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, debug=settings.app_debug)
app.include_router(health_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
