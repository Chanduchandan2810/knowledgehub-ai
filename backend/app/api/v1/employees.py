from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import require_admin_role, UserContext
from app.models.employee import Employee
from pydantic import BaseModel
from app.core.config import settings
from supabase import create_client, Client

class EmployeeCreate(BaseModel):
    email: str
    full_name: str

class EmployeeResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    joined_at: str

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
            "id": emp.auth_user_id,
            "email": emp.email,
            "full_name": emp.full_name,
            "role": "EMPLOYEE",
            "joined_at": emp.created_at.isoformat() if emp.created_at else ""
        })
    return employees

@router.post("", response_model=EmployeeResponse)
async def create_employee(
    emp_in: EmployeeCreate,
    ctx: UserContext = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    supabase_admin: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    )
    
    # Check if employee exists
    result = await db.execute(select(Employee).where(Employee.email == emp_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An employee with this email already exists.")

    try:
        res = supabase_admin.auth.admin.create_user({
            "email": emp_in.email,
            "password": "123456",
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
    await db.commit()
    await db.refresh(new_emp)
    
    return {
        "id": new_emp.auth_user_id,
        "email": new_emp.email,
        "full_name": new_emp.full_name,
        "role": "EMPLOYEE",
        "joined_at": new_emp.created_at.isoformat() if new_emp.created_at else ""
    }
