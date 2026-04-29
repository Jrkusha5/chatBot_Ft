"""Hard ceilings for validation. Tune via env on Settings (must stay <= these caps in code paths)."""

# Chat / JSON
CHAT_MESSAGE_HARD_MAX = 32_000
SESSION_ID_HARD_MAX = 128
FEEDBACK_COMMENT_HARD_MAX = 8_000

# Defaults (Settings env can tighten, not exceed hard max without code change)
DEFAULT_MAX_CHAT_MESSAGE_CHARS = 16_000
DEFAULT_MAX_FEEDBACK_COMMENT_CHARS = 4_000

# Upload / HTTP body
DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MiB
DEFAULT_MAX_JSON_BODY_BYTES = 512 * 1024  # 512 KiB (chat, feedback JSON)
