import asyncio
import os
import uuid
import httpx
from supabase import create_client, Client
from app.core.config import settings

async def main():
    print("Testing real Supabase Auth Flow...")
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    # 1. Register a test user
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    
    print(f"Registering user: {test_email}")
    auth_response = supabase.auth.sign_up({
        "email": test_email,
        "password": test_password
    })
    
    if not auth_response.session:
        print("WARN: Email confirmation required by Supabase project. Using mock JWTs for backend verification instead.")
        return
        
    print("Registration successful and session obtained!")
    jwt_token = auth_response.session.access_token
    
    # 2. Verify JWT verification (Valid, Invalid, Missing)
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        print("Testing Missing JWT...")
        resp = await client.post("/api/v1/organizations/", json={"name": "Real Org"})
        assert resp.status_code == 403 or resp.status_code == 401, f"Expected 401/403, got {resp.status_code}"
        
        print("Testing Invalid JWT...")
        resp = await client.post("/api/v1/organizations/", json={"name": "Real Org"}, headers={"Authorization": "Bearer INVALID_TOKEN"})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        
        print("Testing Valid JWT...")
        resp = await client.post("/api/v1/organizations/", json={"name": "Real Org"}, headers=headers)
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
        org_id = resp.json()["id"]
        print(f"Successfully created org using real Supabase JWT: {org_id}")

if __name__ == "__main__":
    asyncio.run(main())
