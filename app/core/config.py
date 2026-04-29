from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.limits import (
    CHAT_MESSAGE_HARD_MAX,
    DEFAULT_MAX_CHAT_MESSAGE_CHARS,
    DEFAULT_MAX_FEEDBACK_COMMENT_CHARS,
    DEFAULT_MAX_JSON_BODY_BYTES,
    DEFAULT_MAX_UPLOAD_BYTES,
    FEEDBACK_COMMENT_HARD_MAX,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Chat Bot API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    database_url: str = Field(default="sqlite:///./chatbot.db", alias="DATABASE_URL")
    chroma_persist_dir: str = Field(default="./.chroma", alias="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(default="chatbot_knowledge_gemini", alias="CHROMA_COLLECTION_NAME")
    model_name: str = Field(default="gemini-2.0-flash", alias="MODEL_NAME")
    embedding_model: str = Field(default="gemini-embedding-001", alias="EMBEDDING_MODEL")
    top_k: int = Field(default=4, alias="TOP_K")
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    confidence_threshold: float = Field(default=0.4, alias="CONFIDENCE_THRESHOLD")

    max_upload_bytes: int = Field(default=DEFAULT_MAX_UPLOAD_BYTES, alias="MAX_UPLOAD_BYTES")
    max_json_body_bytes: int = Field(default=DEFAULT_MAX_JSON_BODY_BYTES, alias="MAX_JSON_BODY_BYTES")
    max_chat_message_chars: int = Field(
        default=DEFAULT_MAX_CHAT_MESSAGE_CHARS,
        alias="MAX_CHAT_MESSAGE_CHARS",
    )
    max_feedback_comment_chars: int = Field(
        default=DEFAULT_MAX_FEEDBACK_COMMENT_CHARS,
        alias="MAX_FEEDBACK_COMMENT_CHARS",
    )

    @field_validator("max_upload_bytes")
    @classmethod
    def _clamp_upload_bytes(cls, value: int) -> int:
        minimum = 1024 * 1024  # 1 MiB floor
        maximum = 100 * 1024 * 1024  # 100 MiB ceiling
        return max(minimum, min(value, maximum))

    @field_validator("max_json_body_bytes")
    @classmethod
    def _clamp_json_body_bytes(cls, value: int) -> int:
        minimum = 16 * 1024  # 16 KiB
        maximum = 2 * 1024 * 1024  # 2 MiB
        return max(minimum, min(value, maximum))

    @field_validator("max_chat_message_chars")
    @classmethod
    def _clamp_chat_message_chars(cls, value: int) -> int:
        return max(256, min(value, CHAT_MESSAGE_HARD_MAX))

    @field_validator("max_feedback_comment_chars")
    @classmethod
    def _clamp_feedback_comment_chars(cls, value: int) -> int:
        return max(1, min(value, FEEDBACK_COMMENT_HARD_MAX))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
