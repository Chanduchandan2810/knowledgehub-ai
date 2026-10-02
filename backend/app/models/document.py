import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class AccessScope(str, enum.Enum):
    ORGANIZATION = "ORGANIZATION"
    RESTRICTED = "RESTRICTED"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, default=DocumentStatus.UPLOADED.value, nullable=False)
    access_scope = Column(String, default=AccessScope.ORGANIZATION.value, nullable=False, server_default=AccessScope.ORGANIZATION.value)
    
    # Phase 4 Document Processing Fields
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String(500), nullable=True)
    attempt_count = Column(Integer, nullable=False, default=0)
    content_hash = Column(String(64), nullable=True)
    chunk_count = Column(Integer, nullable=True)
    embedding_model = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    __table_args__ = (
        UniqueConstraint("id", "organization_id", name="uq_documents_id_org"),
    )

