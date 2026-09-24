from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.db.session import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.membership import Membership

async def get_current_user(
    payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Try to find user in our DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        user = User(id=user_id, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user

async def get_current_membership(
    x_organization_id: str = Header(..., description="The ID of the organization to access"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Membership:
    # Query membership as superuser (bypassing RLS) to verify access
    result = await db.execute(
        select(Membership)
        .where(Membership.user_id == user.id)
        .where(Membership.organization_id == x_organization_id)
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization"
        )
    
    # Now that access is verified, enforce RLS for all subsequent queries in this session
    await db.execute(text(f"SET LOCAL role = 'authenticated';"))
    await db.execute(text(f"SET LOCAL app.current_tenant = '{membership.organization_id}';"))
    
    return membership

async def require_admin_role(
    membership: Membership = Depends(get_current_membership)
) -> Membership:
    if membership.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return membership
