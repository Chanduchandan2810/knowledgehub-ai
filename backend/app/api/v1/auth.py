from fastapi import APIRouter, Depends
from app.api.deps import get_current_user_context, UserContext

router = APIRouter()

@router.get("/me")
async def get_my_context(ctx: UserContext = Depends(get_current_user_context)):
    return {
        "role": ctx.role,
        "organization_id": str(ctx.organization_id),
        "auth_user_id": str(ctx.auth_user_id),
        "full_name": ctx.full_name,
        "email": ctx.email
    }
