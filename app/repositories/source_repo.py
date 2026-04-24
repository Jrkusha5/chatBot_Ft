from sqlalchemy.orm import Session

from app.db.models.source import Source


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_source(
        self,
        *,
        source_type: str,
        name: str,
        location: str,
        content_hash: str,
        chunks_indexed: int,
    ) -> Source:
        source = Source(
            source_type=source_type,
            name=name,
            location=location,
            content_hash=content_hash,
            chunks_indexed=chunks_indexed,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source
