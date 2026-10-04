from pydantic import BaseModel, ConfigDict
from typing import List
import uuid
from datetime import datetime

class ConversationBase(BaseModel):
    title: str | None = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    
    model_config = ConfigDict(from_attributes=True)

