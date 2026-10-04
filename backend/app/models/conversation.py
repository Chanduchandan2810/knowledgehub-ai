import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    auth_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))
