import jwt
from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from supabase import create_client, Client

security = HTTPBearer(auto_error=False)

# Initialize a single Supabase client for the backend
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def verify_token(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    token = credentials.credentials
    try:
        # Securely verify token and get user from Supabase Auth Server directly with retry for transient pool disconnects
        try:
            user_response = supabase.auth.get_user(token)
        except Exception:
            user_response = supabase.auth.get_user(token)

        user = user_response.user
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        return {
            "sub": user.id,
            "email": user.email,
            "user_metadata": user.user_metadata or {}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed: {str(e)}")
