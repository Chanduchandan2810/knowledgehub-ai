from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import verify_token
from app.api.deps import get_current_user_context, UserContext
from app.models.organization import Organization
from app.models.admin import Admin
from app.schemas.organization import OrganizationCreate, OrganizationResponse
import uuid

router = APIRouter()

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: OrganizationCreate,
    payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    auth_user_id = payload.get("sub")
    email = payload.get("email", "")
    user_metadata = payload.get("user_metadata", {})
    full_name = user_metadata.get("full_name", "Admin")

    if not auth_user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check if the user is already an admin
    existing = await db.execute(select(Admin).where(Admin.auth_user_id == auth_user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already associated with an organization")

    # Create the organization
    org = Organization(**org_in.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    # Create the ADMIN record for the creator
    admin = Admin(
        auth_user_id=auth_user_id,
        organization_id=org.id,
        full_name=full_name,
        email=email
    )
    db.add(admin)
    await db.commit()
    
    return org

@router.get("/current", response_model=OrganizationResponse)
async def get_current_organization(
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Organization).where(Organization.id == ctx.organization_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
