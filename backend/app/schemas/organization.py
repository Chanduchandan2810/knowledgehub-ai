from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


