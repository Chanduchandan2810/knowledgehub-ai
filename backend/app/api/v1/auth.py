from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user_context, UserContext
from app.core.security import supabase

router = APIRouter()

class DemoStartRequest(BaseModel):
    role: str

@router.post("/demo/start")
async def start_demo(request: DemoStartRequest):
    if request.role not in ("ADMIN", "EMPLOYEE"):
        raise HTTPException(status_code=400, detail="Invalid demo role")
        
    email = "admin@demo.knowledgehub.local" if request.role == "ADMIN" else "employee@demo.knowledgehub.local"
    
    try:
        # Sign in using the fixed demo credentials to generate a real Supabase session
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": "SecureDemoPassword123!"
        })
        
        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "expires_in": auth_response.session.expires_in,
            "role": request.role
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate demo session: {str(e)}")

@router.get("/me")
async def get_my_context(ctx: UserContext = Depends(get_current_user_context)):
    return {
        "role": ctx.role,
        "organization_id": str(ctx.organization_id),
        "auth_user_id": str(ctx.auth_user_id),
        "full_name": ctx.full_name,
        "email": ctx.email
    }
