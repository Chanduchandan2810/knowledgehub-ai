import uuid
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))
