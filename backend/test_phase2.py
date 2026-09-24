import asyncio
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text, select
import httpx
import uuid

from app.core.config import settings

async def test_all():
    print("Generating mock JWTs...")
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    token1 = jwt.encode(
        {"sub": user1_id, "email": f"{user1_id}@test.com", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256"
    )
    
    token2 = jwt.encode(
        {"sub": user2_id, "email": f"{user2_id}@test.com", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256"
    )
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        print("Testing unauthenticated access...")
        resp = await client.get("/api/v1/organizations/me")
        assert resp.status_code == 403 or resp.status_code == 401, f"Expected 401/403, got {resp.status_code}"
        
        print("Testing create organization for User 1...")
        resp = await client.post("/api/v1/organizations/", json={"name": "Org 1"}, headers=headers1)
        assert resp.status_code == 201
        org1_id = resp.json()["id"]
        print(f"Created Org 1: {org1_id}")

        print("Testing create organization for User 2...")
        resp = await client.post("/api/v1/organizations/", json={"name": "Org 2"}, headers=headers2)
        assert resp.status_code == 201
        org2_id = resp.json()["id"]
        print(f"Created Org 2: {org2_id}")

        print("Testing Tenant Isolation: User 1 trying to access Org 2...")
        headers1_org2 = {"Authorization": f"Bearer {token1}", "x-organization-id": org2_id}
        resp = await client.get("/api/v1/organizations/current", headers=headers1_org2)
        assert resp.status_code == 403, f"Expected 403 Forbidden, got {resp.status_code}"
        
        print("Testing Tenant Isolation: User 1 trying to access Org 1...")
        headers1_org1 = {"Authorization": f"Bearer {token1}", "x-organization-id": org1_id}
        resp = await client.get("/api/v1/organizations/current", headers=headers1_org1)
        assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
        assert resp.json()["id"] == org1_id
        
        print("ALL TESTS PASSED: Authentication, Tenant Isolation, and Organization routing work perfectly!")

if __name__ == "__main__":
    asyncio.run(test_all())
