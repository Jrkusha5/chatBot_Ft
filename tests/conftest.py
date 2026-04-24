import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_chatbot.db"
os.environ["CHROMA_PERSIST_DIR"] = "./.chroma_test"
os.environ["OPENAI_API_KEY"] = "test-key"

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

get_settings.cache_clear()

engine = create_engine("sqlite:///./test_chatbot.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
