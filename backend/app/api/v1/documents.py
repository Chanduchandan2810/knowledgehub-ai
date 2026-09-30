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
    
    # 1. Validate file size and content
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    
    # Validate MIME type and verify file signature
    mime_type = file.content_type
    filename_lower = file.filename.lower()
    if filename_lower.endswith(".pdf") or mime_type == "application/pdf":
        if not file_bytes.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Invalid PDF file. Header signature mismatch.")
        mime_type = "application/pdf"
    elif filename_lower.endswith(".txt") or mime_type == "text/plain":
        try:
            file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid text file. Must be UTF-8 encoded text.")
        mime_type = "text/plain"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and TXT are allowed.")

    # 2. Create document ID & Storage Path
    doc_id = uuid.uuid4()
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in " .-_").strip()
    if not safe_filename:
        safe_filename = f"doc_{doc_id}.pdf" if mime_type == "application/pdf" else f"doc_{doc_id}.txt"
    storage_path = f"organizations/{ctx.organization_id}/documents/{doc_id}/{safe_filename}"

    # 3. Upload to storage
    try:
        await upload_document_to_storage(file_bytes, storage_path, mime_type)
    except Exception as e:
        logger.error(f"Storage upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document to storage")

    # 4. Create database record
    new_doc = Document(
        id=doc_id,
        organization_id=ctx.organization_id,
        uploaded_by=ctx.user_id,
        filename=safe_filename,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size=file_size,
        status=DocumentStatus.UPLOADED.value
    )
    db.add(new_doc)
    try:
        await db.flush()
        # Capture the database-generated values before committing
        from app.schemas.document import DocumentResponse
        response = DocumentResponse.model_validate(new_doc)
        await db.commit()
    except Exception as e:
        await db.rollback()
        # Clean up storage if DB insert or commit fails
        try:
            await delete_document_from_storage(storage_path)
        except Exception as se:
            logger.error(f"Failed to cleanup storage after DB error: {se}")
        logger.error(f"Database insert/commit failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save document metadata")
        
    return response

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
        
    storage_path = doc.storage_path

    # 1. Delete from DB first (document_permissions cascade on delete)
    await db.delete(doc)
    await db.commit()

    # 2. Delete corresponding Storage object
    try:
        await delete_document_from_storage(storage_path)
    except Exception as e:
        logger.error(f"Storage delete failed for path {storage_path} after DB record was deleted: {e}")
        # Note: We do not fail the request or recreate the DB record, as the metadata is already purged.
        # The orphaned file can be cleaned up via background reconciliation.

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
        (Employee.id == data.employee_id) | (Employee.auth_user_id == data.employee_id),
        Employee.organization_id == ctx.organization_id
    )
    result = await db.execute(emp_query)
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found or belongs to another organization")
        
    new_perm = DocumentPermission(
        document_id=document_id,
        employee_id=emp.id
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
        
    # Resolve target employee (either by id or auth_user_id)
    emp_query = select(Employee).where(
        (Employee.id == employee_id) | (Employee.auth_user_id == employee_id),
        Employee.organization_id == ctx.organization_id
    )
    emp = (await db.execute(emp_query)).scalar_one_or_none()
    target_emp_id = emp.id if emp else employee_id

    # Find and delete
    perm_query = select(DocumentPermission).where(
        DocumentPermission.document_id == document_id,
        DocumentPermission.employee_id == target_emp_id
    )
    perm = (await db.execute(perm_query)).scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
        
    await db.delete(perm)
    await db.commit()
    return None

