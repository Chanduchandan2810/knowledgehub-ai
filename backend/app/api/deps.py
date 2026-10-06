import uuid
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_token
from app.models.admin import Admin
from app.models.employee import Employee
from pydantic import BaseModel

class UserContext(BaseModel):
    user_id: uuid.UUID
    auth_user_id: uuid.UUID
    organization_id: uuid.UUID
    role: str
    email: str
    full_name: str

async def get_current_user_context(
    request: Request,
    payload: dict = Depends(verify_token),
    x_organization_id: uuid.UUID = Header(None, description="The ID of the organization to access"),
    db: AsyncSession = Depends(get_db)
) -> UserContext:
    auth_user_id = payload.get("sub")
    if not auth_user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Bypass RLS to find the user's role and organization
    # First check Admin
    admin_query = select(Admin).where(Admin.auth_user_id == auth_user_id)
    if x_organization_id:
        admin_query = admin_query.where(Admin.organization_id == x_organization_id)
    
    result = await db.execute(admin_query)
    admin = result.scalar_one_or_none()
    
    if admin:
        ctx = UserContext(
            user_id=admin.id,
            auth_user_id=admin.auth_user_id,
            organization_id=admin.organization_id,
            role="ADMIN",
            email=admin.email,
            full_name=admin.full_name
        )
    else:
        # Check Employee
        emp_query = select(Employee).where(Employee.auth_user_id == auth_user_id)
        if x_organization_id:
            emp_query = emp_query.where(Employee.organization_id == x_organization_id)
            
        result = await db.execute(emp_query)
        emp = result.scalar_one_or_none()
        
        if emp:
            ctx = UserContext(
                user_id=emp.id,
                auth_user_id=emp.auth_user_id,
                organization_id=emp.organization_id,
                role="EMPLOYEE",
                email=emp.email,
                full_name=emp.full_name
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to any organization"
            )
            
    # Apply RLS context
    await db.execute(text(f"SET LOCAL role = 'authenticated';"))
    await db.execute(text(f"SET LOCAL app.current_tenant = '{ctx.organization_id}';"))
    
    request.state.user_context = ctx
    return ctx

async def require_admin_role(
    ctx: UserContext = Depends(get_current_user_context)
) -> UserContext:
    if ctx.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return ctx
import time

_rate_limits = {}

class RateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window

    async def __call__(self, request: Request, ctx: UserContext = Depends(get_current_user_context)):
        is_demo = ctx.organization_id == settings.DEMO_ORG_ID
        limit = max(1, self.requests // 2) if is_demo else self.requests

        now = time.time()
        key = (str(ctx.user_id), request.url.path)
        
        count, reset_time = _rate_limits.get(key, (0, 0))
        if now > reset_time:
            count = 0
            reset_time = now + self.window
            
        if count >= limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
        _rate_limits[key] = (count + 1, reset_time)
