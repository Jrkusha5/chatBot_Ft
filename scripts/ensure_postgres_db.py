#!/usr/bin/env python3
"""Create the PostgreSQL database from DATABASE_URL if it does not exist.

Connects to the built-in ``postgres`` maintenance database, then runs
``CREATE DATABASE`` for the target name. Run once before ``alembic upgrade head``.

Usage (from repo root, venv active):

    python scripts/ensure_postgres_db.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

from app.core.config import get_settings

_SAFE_IDENT = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def main() -> int:
    settings = get_settings()
    url = make_url(settings.database_url)
    if url.get_dialect().name != "postgresql":
        print("DATABASE_URL is not PostgreSQL; nothing to do.", file=sys.stderr)
        return 0

    dbname = url.database
    if not dbname:
        print("DATABASE_URL has no database name in the path.", file=sys.stderr)
        return 1

    if not _SAFE_IDENT.match(dbname):
        print(f"Refusing non-alphanumeric database name: {dbname!r}", file=sys.stderr)
        return 1

    admin_url = url.set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": dbname},
        ).scalar()
        if exists:
            print(f"Database {dbname!r} already exists.")
            return 0

        conn.execute(text(f'CREATE DATABASE "{dbname}"'))
        print(f"Created database {dbname!r}.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
