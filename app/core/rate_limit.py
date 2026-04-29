"""Rate limiting for expensive endpoints (slowapi)."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import get_settings


def chat_session_bucket(request: Request) -> str:
    """Bucket per X-Chat-Session-Id when set; otherwise per client IP."""
    sid = (request.headers.get("X-Chat-Session-Id") or "").strip()[:128]
    if sid:
        return f"chat_session:{sid}"
    return f"chat_ip:{get_remote_address(request)}"


def dynamic_chat_ip_limit(*_args: object, **_kwargs: object) -> str:
    return get_settings().rate_limit_chat_per_ip


def dynamic_chat_session_limit(*_args: object, **_kwargs: object) -> str:
    return get_settings().rate_limit_chat_per_session


def dynamic_ingest_ip_limit(*_args: object, **_kwargs: object) -> str:
    return get_settings().rate_limit_ingest_per_ip


limiter = Limiter(key_func=get_remote_address)
