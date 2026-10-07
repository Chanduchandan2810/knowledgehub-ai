from typing import List
import uuid
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import require_admin_role, UserContext, RateLimiter
from app.models.employee import Employee
from app.models.document import Document, AccessScope
from app.models.document_permission import DocumentPermission
from pydantic import BaseModel
from app.core.config import settings
from supabase import create_client, Client

class EmployeeCreate(BaseModel):
    email: str
    full_name: str

class EmployeeResponse(BaseModel):
    id: uuid.UUID
    auth_user_id: uuid.UUID
    email: str
    full_name: str
    role: str
    joined_at: str
    temporary_password: str | None = None

    class Config:
        from_attributes = True

router = APIRouter()

@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Employee).where(Employee.organization_id == ctx.organization_id)
    )
    employees = []
    for emp in result.scalars().all():
        employees.append({
            "id": emp.id,
            "auth_user_id": emp.auth_user_id,
            "email": emp.email,
            "full_name": emp.full_name,
            "role": "EMPLOYEE",
            "joined_at": emp.created_at.isoformat() if emp.created_at else "",
            "temporary_password": None
        })
    return employees

@router.post("", response_model=EmployeeResponse)
async def create_employee(
    emp_in: EmployeeCreate,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
    rate_limit: None = Depends(RateLimiter(requests=10, window=60))
):
    supabase_admin: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    )
    
    # Check if employee exists
    result = await db.execute(select(Employee).where(Employee.email == emp_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An employee with this email already exists.")

    temp_password = secrets.token_urlsafe(32)

    try:
        res = supabase_admin.auth.admin.create_user({
            "email": emp_in.email,
            "password": temp_password,
            "email_confirm": True
        })
        auth_user_id = res.user.id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create Auth user: {str(e)}")

    new_emp = Employee(
        auth_user_id=auth_user_id,
        organization_id=ctx.organization_id,
        full_name=emp_in.full_name,
        email=emp_in.email
    )
    db.add(new_emp)
    await db.flush()
    
    # Grant access to all ORGANIZATION scope documents in this org
    docs_query = select(Document.id).where(
        Document.organization_id == ctx.organization_id,
        Document.access_scope == AccessScope.ORGANIZATION.value
    )
    org_doc_ids = (await db.execute(docs_query)).scalars().all()
    for doc_id in org_doc_ids:
        db.add(DocumentPermission(
            document_id=doc_id,
            employee_id=new_emp.id
        ))

    await db.commit()
    await db.refresh(new_emp)
    
    return {
        "id": new_emp.id,
        "auth_user_id": new_emp.auth_user_id,
        "email": new_emp.email,
        "full_name": new_emp.full_name,
        "role": "EMPLOYEE",
        "joined_at": new_emp.created_at.isoformat() if new_emp.created_at else "",
        "temporary_password": temp_password
    }
