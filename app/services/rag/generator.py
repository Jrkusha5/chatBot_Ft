from app.core.config import get_settings
from app.services.gemini_client import get_gemini_client


def generate_answer(prompt: str) -> str:
    settings = get_settings()
    client = get_gemini_client()

    response = client.models.generate_content(
        model=settings.model_name,
        contents=prompt,
        config={
            "system_instruction": (
                "You answer questions using only the provided context in the user message. "
                "If the context is insufficient, say you don't know."
            ),
            "temperature": 0.2,
        },
    )
    text = response.text
    return text.strip() if text else "I don't know based on available context."
