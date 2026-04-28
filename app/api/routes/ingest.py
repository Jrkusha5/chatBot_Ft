import hashlib

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.source_repo import SourceRepository
from app.schemas.ingest import IngestResponse
from app.services.ingestion.chunker import ChunkPayload, chunk_text_with_metadata
from app.services.ingestion.cleaner import clean_text
from app.services.ingestion.embedder import embed_texts
from app.services.ingestion.indexer import index_chunks
from app.services.ingestion.loaders import extract_text_from_file
from app.services.telemetry.metrics import metrics_store

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/file", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> IngestResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        segments, source_type = extract_text_from_file(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunk_payloads: list[ChunkPayload] = []
    for segment in segments:
        cleaned = clean_text(segment.text)
        if not cleaned:
            continue
        chunk_payloads.extend(
            chunk_text_with_metadata(
                cleaned,
                page=segment.page,
                section=segment.section,
            )
        )

    if not chunk_payloads:
        raise HTTPException(status_code=400, detail="No usable text extracted from file")

    content_hash = hashlib.sha256(content).hexdigest()
    source_repo = SourceRepository(db)
    source = source_repo.create_source(
        source_type=source_type,
        name=file.filename,
        location=f"upload://{file.filename}",
        content_hash=content_hash,
        chunks_indexed=0,
    )

    chunks = [payload.content for payload in chunk_payloads]
    embeddings = embed_texts(chunks)
    total_chunks = index_chunks(
        source_id=source.id,
        source_name=source.name,
        source_type=source.source_type,
        chunks=chunks,
        embeddings=embeddings,
        chunk_metadatas=[
            {
                "page": payload.page,
                "section": payload.section,
            }
            for payload in chunk_payloads
        ],
    )

    source.chunks_indexed = total_chunks
    db.add(source)
    db.commit()
    db.refresh(source)
    metrics_store.observe_ingest_request()

    return IngestResponse(
        source_id=source.id,
        source_name=source.name,
        source_type=source.source_type,
        chunks_indexed=source.chunks_indexed,
        status="indexed",
    )
