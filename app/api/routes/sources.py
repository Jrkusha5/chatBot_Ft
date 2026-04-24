from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.source_repo import SourceRepository
from app.schemas.source import SourceDeleteResponse, SourceResponse
from app.vectorstore.collection_manager import ensure_default_collection

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)) -> list[SourceResponse]:
    repo = SourceRepository(db)
    sources = repo.list_sources()
    return [
        SourceResponse(
            id=source.id,
            source_type=source.source_type,
            name=source.name,
            location=source.location,
            chunks_indexed=source.chunks_indexed,
            created_at=source.created_at,
        )
        for source in sources
    ]


@router.delete("/{source_id}", response_model=SourceDeleteResponse, status_code=status.HTTP_200_OK)
def delete_source(source_id: str, db: Session = Depends(get_db)) -> SourceDeleteResponse:
    repo = SourceRepository(db)
    source = repo.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    collection = ensure_default_collection()
    collection.delete(where={"source_id": source_id})
    repo.delete_source(source)

    return SourceDeleteResponse(source_id=source_id, status="deleted")
