import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user_context, require_admin_role, UserContext
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_permission import DocumentPermission
from app.models.admin import Admin
from app.models.employee import Employee
from app.schemas.document import (
    DocumentResponse, 
    DocumentPermissionResponse, 
    DocumentPermissionCreate
)
from app.core.storage import upload_document_to_storage, delete_document_from_storage

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_MIME_TYPES = ["application/pdf", "text/plain"]

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
    
    # 1. Validate file size and type
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    
    # Use content_type but fallback to basic extension check
    mime_type = file.content_type
    if not mime_type or mime_type not in ALLOWED_MIME_TYPES:
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and TXT are allowed.")
        mime_type = "application/pdf" if file.filename.lower().endswith('.pdf') else "text/plain"

    # 2. Get admin user id for uploaded_by
    result = await db.execute(select(Admin).where(Admin.auth_user_id == ctx.auth_user_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=500, detail="Admin record not found.")

    # 3. Create document ID & Storage Path
    doc_id = uuid.uuid4()
    # Simple safe filename - just remove weird chars or use UUID. We'll use uuid for uniqueness
    # organizations/{org_id}/documents/{doc_id}/filename.pdf
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in " .-_")
    storage_path = f"organizations/{ctx.organization_id}/documents/{doc_id}/{safe_filename}"

    # 4. Upload to storage
    try:
        await upload_document_to_storage(file_bytes, storage_path, mime_type)
    except Exception as e:
        logger.error(f"Storage upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document to storage")

    # 5. Create database record
    new_doc = Document(
        id=doc_id,
        organization_id=ctx.organization_id,
        uploaded_by=admin.id,
        filename=safe_filename,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size=file_size,
        status=DocumentStatus.UPLOADED.value
    )
    db.add(new_doc)
    try:
        await db.commit()
        await db.refresh(new_doc)
    except Exception as e:
        await db.rollback()
        # Attempt to clean up storage if DB fails
        try:
            await delete_document_from_storage(storage_path)
        except:
            pass
        logger.error(f"Database insert failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save document metadata")
        
    return new_doc

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).where(Document.organization_id == ctx.organization_id).order_by(Document.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).where(
        Document.id == document_id, 
        Document.organization_id == ctx.organization_id
    )
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    # Find document
    query = select(Document).where(
        Document.id == document_id, 
        Document.organization_id == ctx.organization_id
    )
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from storage first
    try:
        await delete_document_from_storage(doc.storage_path)
    except Exception as e:
        logger.error(f"Storage delete failed: {e}")
        # We may still want to delete the DB record if it's orphaned, but usually we halt.
        # Let's halt to prevent DB and Storage getting fully out of sync without manual intervention.
        raise HTTPException(status_code=500, detail="Failed to delete document from storage")

    # Delete from DB (document_permissions cascade on delete)
    await db.delete(doc)
    await db.commit()
    return None


@router.get("/{document_id}/permissions", response_model=List[DocumentPermissionResponse])
async def list_document_permissions(
    document_id: uuid.UUID,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    # Verify document ownership
    doc_query = select(Document).where(
        Document.id == document_id, 
        Document.organization_id == ctx.organization_id
    )
    if not (await db.execute(doc_query)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")
        
    perm_query = select(DocumentPermission).where(DocumentPermission.document_id == document_id)
    result = await db.execute(perm_query)
    return result.scalars().all()


@router.post("/{document_id}/permissions", response_model=DocumentPermissionResponse, status_code=status.HTTP_201_CREATED)
async def add_document_permission(
    document_id: uuid.UUID,
    data: DocumentPermissionCreate,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    if document_id != data.document_id:
        raise HTTPException(status_code=400, detail="Mismatched document ID")

    # Verify document ownership
    doc_query = select(Document).where(
        Document.id == document_id, 
        Document.organization_id == ctx.organization_id
    )
    if not (await db.execute(doc_query)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Verify employee exists and belongs to the SAME organization
    emp_query = select(Employee).where(
        Employee.id == data.employee_id,
        Employee.organization_id == ctx.organization_id
    )
    if not (await db.execute(emp_query)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Employee not found or belongs to another organization")
        
    new_perm = DocumentPermission(
        document_id=document_id,
        employee_id=data.employee_id
    )
    db.add(new_perm)
    try:
        await db.commit()
        await db.refresh(new_perm)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Permission already exists")
        
    return new_perm


@router.delete("/{document_id}/permissions/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document_permission(
    document_id: uuid.UUID,
    employee_id: uuid.UUID,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    # Verify document ownership
    doc_query = select(Document).where(
        Document.id == document_id, 
        Document.organization_id == ctx.organization_id
    )
    if not (await db.execute(doc_query)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Find and delete
    perm_query = select(DocumentPermission).where(
        DocumentPermission.document_id == document_id,
        DocumentPermission.employee_id == employee_id
    )
    perm = (await db.execute(perm_query)).scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
        
    await db.delete(perm)
    await db.commit()
    return None

