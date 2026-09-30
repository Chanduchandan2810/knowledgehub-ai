from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.document import DocumentStatus

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
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentPermissionBase(BaseModel):
    employee_id: UUID

class DocumentPermissionCreate(DocumentPermissionBase):
    document_id: UUID

class DocumentPermissionResponse(DocumentPermissionBase):
    id: UUID
    document_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
