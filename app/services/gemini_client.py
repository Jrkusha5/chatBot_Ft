from google import genai

from app.core.config import get_settings


def get_gemini_client() -> genai.Client:
    settings = get_settings()
    key = (settings.gemini_api_key or "").strip()
    if not key:
        raise ValueError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=key)
