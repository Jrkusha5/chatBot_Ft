from chromadb.api.models.Collection import Collection

from app.core.config import get_settings
from app.vectorstore.chroma_client import get_chroma_client


def ensure_collection(name: str) -> Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)


def ensure_default_collection() -> Collection:
    settings = get_settings()
    return ensure_collection(settings.chroma_collection_name)


def get_collection(name: str) -> Collection:
    client = get_chroma_client()
    return client.get_collection(name=name)


def list_collections() -> list[str]:
    client = get_chroma_client()
    return [collection.name for collection in client.list_collections()]


def delete_collection(name: str) -> None:
    client = get_chroma_client()
    client.delete_collection(name=name)
