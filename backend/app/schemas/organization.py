from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str

class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MembershipResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: str
    
    model_config = ConfigDict(from_attributes=True)
