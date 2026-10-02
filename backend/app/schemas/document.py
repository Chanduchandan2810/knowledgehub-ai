from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.document import DocumentStatus, AccessScope

class DocumentBase(BaseModel):
    filename: str
    mime_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    organization_id: UUID
    uploaded_by: UUID
    storage_path: str

class DocumentResponse(DocumentBase):
    id: UUID
    organization_id: UUID
    uploaded_by: Optional[UUID]
    status: DocumentStatus
    access_scope: AccessScope = AccessScope.ORGANIZATION
    
    # Phase 4 fields
    processing_started_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    attempt_count: int = 0
    chunk_count: Optional[int] = None
    embedding_model: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentScopeUpdate(BaseModel):
    access_scope: AccessScope

class DocumentPermissionBase(BaseModel):
    employee_id: UUID | None = None
    admin_id: UUID | None = None

class DocumentPermissionCreate(DocumentPermissionBase):
    document_id: UUID

class DocumentPermissionResponse(DocumentPermissionBase):
    id: UUID
    document_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentReprocessResponse(BaseModel):
    message: str
    document_id: UUID
    status: DocumentStatus
