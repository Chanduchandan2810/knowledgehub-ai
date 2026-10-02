import uuid
from sqlalchemy import Column, DateTime, ForeignKey, text, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id", ondelete="CASCADE"), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    __table_args__ = (
        UniqueConstraint("document_id", "employee_id", name="uq_document_employee_permission"),
        UniqueConstraint("document_id", "admin_id", name="uq_document_admin_permission"),
        CheckConstraint("num_nonnulls(employee_id, admin_id) = 1", name="chk_one_identity"),
    )
