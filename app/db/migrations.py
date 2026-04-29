from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.core.config import get_settings


def run_migrations() -> None:
    project_root = Path(__file__).resolve().parents[2]
    alembic_ini = project_root / "alembic.ini"
    if not alembic_ini.exists():
        raise FileNotFoundError(f"Alembic config not found at {alembic_ini}")

    config = Config(str(alembic_ini))
    db_url = get_settings().database_url
    engine = create_engine(db_url, pool_pre_ping=True)
    try:
        inspector = inspect(engine)
        has_version_table = inspector.has_table("alembic_version")
        has_existing_schema = inspector.has_table("chat_sessions")
    finally:
        engine.dispose()

    # Existing databases created before Alembic should be baseline-stamped once.
    if not has_version_table and has_existing_schema:
        command.stamp(config, "head")
        return

    command.upgrade(config, "head")
