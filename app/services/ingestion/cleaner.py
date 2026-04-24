import re


def clean_text(text: str) -> str:
    normalized = text.replace("\x00", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()
