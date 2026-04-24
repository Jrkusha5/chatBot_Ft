from openai import OpenAI

from app.core.config import get_settings


def generate_answer(prompt: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.model_name,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You answer questions using provided context."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or "I don't know based on available context."
