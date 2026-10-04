import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class MessageRole(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), index=True)
