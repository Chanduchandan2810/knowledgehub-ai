import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text, JSON, ForeignKeyConstraint, UniqueConstraint, Computed
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    
    page_number = Column(Integer, nullable=True)
    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=False)
    
    metadata_json = Column(JSON, default={}, nullable=False)
    
    # TSVector is generated in DB, so we often don't write to it from ORM directly
    content_tsv = Column(TSVECTOR, Computed("to_tsvector('english', content)", persisted=True))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    __table_args__ = (
        ForeignKeyConstraint(
            ["document_id", "organization_id"],
            ["documents.id", "documents.organization_id"],
            ondelete="CASCADE",
            name="fk_chunk_document"
        ),
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
    )
