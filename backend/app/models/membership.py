import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Membership(Base):
    __tablename__ = "memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False) # 'ADMIN', 'KNOWLEDGE_MANAGER', 'MEMBER'
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
    )

    user = relationship("User")
    organization = relationship("Organization")
