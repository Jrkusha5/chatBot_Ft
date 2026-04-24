from pathlib import Path

import chromadb
from chromadb.api import ClientAPI

from app.core.config import get_settings


def get_chroma_client() -> ClientAPI:
    settings = get_settings()
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))
