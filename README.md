# AI Chat Bot

A **Retrieval-Augmented Generation (RAG)** HTTP API: upload documents, embed them into a vector store, and chat with an LLM that answers from your indexed content—with citations, session history, and basic telemetry.

Built with **FastAPI**, **Google Gemini** (generation + embeddings), **ChromaDB** (local persistence), and **SQLAlchemy** + **Alembic** for relational data (sessions, messages, sources, feedback).

---

## What it does

1. **Ingestion** — Accepts `.pdf`, `.txt`, and `.md` files. Text is cleaned, chunked, embedded with Gemini, and stored in ChromaDB. Source metadata is recorded in the database.
2. **Chat** — Retrieves relevant chunks, applies a confidence threshold, and either answers with Gemini using retrieved context or returns a safe “I don’t know…” response when context is weak or missing.
3. **Operations** — List/delete indexed sources, submit user feedback, and read in-process request/chat metrics.

Rate limiting (per IP and per chat session), request size limits, and structured logging are included for safer defaults in development and production.

---

## Requirements

| Item | Notes |
|------|--------|
| **Python** | 3.11+ recommended (matches project bytecode targets). |
| **Gemini API key** | Required for embeddings and chat answers. [Google AI Studio](https://aistudio.google.com/) |
| **Database** | Use **PostgreSQL** in production via `DATABASE_URL`. |
| **Disk** | ChromaDB persists under `CHROMA_PERSIST_DIR` (default `./.chroma`). |

---

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Configuration

1. Copy the example environment file and edit values:

   ```bash
   cp .env.example .env
   ```

2. Set at least **`GEMINI_API_KEY`**. For PostgreSQL instead of SQLite, set **`DATABASE_URL`** (see `.env.example`).

Other important variables (all documented in `.env.example`):

- **`CHROMA_PERSIST_DIR`**, **`CHROMA_COLLECTION_NAME`**
- **`MODEL_NAME`**, **`EMBEDDING_MODEL`**
- **`TOP_K`**, **`CHUNK_SIZE`**, **`CHUNK_OVERLAP`**, **`CONFIDENCE_THRESHOLD`**
- Optional caps and rate limits: `MAX_*`, `RATE_LIMIT_*`

On startup the app runs **Alembic migrations** to head (or stamps existing DBs when upgrading from pre-Alembic schemas), initializes the DB session factory, and ensures the default Chroma collection exists.

---

## Running the server

From the project root (where `main.py` re-exports the FastAPI app):

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Health:** `GET http://127.0.0.1:8000/health`
- **Interactive docs:** `http://127.0.0.1:8000/docs` (Swagger UI)
- **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`

---

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness / basic app info |
| `POST` | `/ingest/file` | Multipart upload; index a document |
| `POST` | `/chat` | RAG chat; returns `session_id`, `answer`, `confidence`, `citations` |
| `GET` | `/sources` | List indexed sources |
| `DELETE` | `/sources/{source_id}` | Remove a source from DB and vector store |
| `POST` | `/feedback` | Store user feedback on a session / message |
| `GET` | `/metrics` | Snapshot of in-memory telemetry counters |

Request/response shapes are defined in `app/schemas/` and visible in `/docs`.

---

## Testing

```bash
pytest
```

Tests live under `tests/` and use fixtures from `tests/conftest.py`.

---

## Project layout (high level)

| Path | Role |
|------|------|
| `main.py` | ASGI entry: imports `app` from `app.main` |
| `app/main.py` | FastAPI app, middleware, routers, startup |
| `app/api/routes/` | HTTP route handlers |
| `app/services/` | RAG, ingestion, Gemini client, retrieval |
| `app/vectorstore/` | Chroma client and collection helpers |
| `app/db/` | SQLAlchemy models, session, migrations hook |
| `alembic/` | Database migration revisions |
| `tests/` | Pytest suite |

---

## Production notes

- Set **`APP_ENV=production`** and supply secrets via the host environment or a secret manager—**do not commit `.env`** with real keys.
- Prefer **PostgreSQL** and a stable **`CHROMA_PERSIST_DIR`** on durable storage.
- Review rate limits and body/upload size settings for your traffic profile.

---

## License

No license file is present in this repository; add one if you intend to distribute or open-source the project.
