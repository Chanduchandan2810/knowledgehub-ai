from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_membership
from app.models.user import User
from app.models.organization import Organization
from app.models.membership import Membership
from app.schemas.organization import OrganizationCreate, OrganizationResponse, MembershipResponse

router = APIRouter()

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create the organization
    org = Organization(name=org_in.name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    # Create the ADMIN membership for the creator
    membership = Membership(
        user_id=current_user.id,
        organization_id=org.id,
        role="ADMIN"
    )
    db.add(membership)
    await db.commit()
    
    return org

@router.get("/me", response_model=List[OrganizationResponse])
async def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch all organizations the user is a member of
    result = await db.execute(
        select(Organization)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/current", response_model=OrganizationResponse)
async def get_current_organization(
    membership: Membership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db)
):
    # This endpoint tests tenant isolation via the get_current_membership dependency
    # It requires the x-organization-id header and returns the org if authorized
    result = await db.execute(select(Organization).where(Organization.id == membership.organization_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
