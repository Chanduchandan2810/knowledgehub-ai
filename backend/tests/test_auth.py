import pytest
import jwt
from datetime import datetime, timedelta, timezone
import httpx
import uuid
import sqlalchemy

from app.core.config import settings
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.security import verify_token
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security

pytestmark = pytest.mark.asyncio

@pytest.fixture
def generate_jwt():
    def _generate(user_id, email, full_name="Test User"):
        return jwt.encode(
            {
                "sub": user_id,
                "email": email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "user_metadata": {"full_name": full_name}
            },
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256"
        )
    return _generate

async def test_invalid_jwt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer INVALID_TOKEN"})
        assert resp.status_code == 401

async def test_missing_jwt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401 or resp.status_code == 403

async def test_auth_and_organization_isolation(generate_jwt):
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import text
    from fastapi import HTTPException, Security
    from fastapi.security import HTTPAuthorizationCredentials
    from app.core.security import verify_token, security

    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        await db.execute(text(f"INSERT INTO auth.users (id) VALUES ('{user_a_id}') ON CONFLICT DO NOTHING"))
        await db.execute(text(f"INSERT INTO auth.users (id) VALUES ('{user_b_id}') ON CONFLICT DO NOTHING"))
        await db.commit()

    token_a = "admin_token_a"
    token_b = "admin_token_b"

    def override_verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
        if credentials.credentials == "admin_token_a":
            return {"sub": user_a_id, "email": f"admin_a_{user_a_id}@test.com", "user_metadata": {"full_name": "Admin A"}}
        if credentials.credentials == "admin_token_b":
            return {"sub": user_b_id, "email": f"admin_b_{user_b_id}@test.com", "user_metadata": {"full_name": "Admin B"}}
        raise HTTPException(status_code=401, detail="Invalid token")

    app.dependency_overrides[verify_token] = override_verify_token

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_a = await client.post(
                "/api/v1/organizations",
                json={"name": "Org A"},
                headers={"Authorization": f"Bearer {token_a}"}
            )
            assert resp_a.status_code == 201
            org_a_id = resp_a.json()["id"]

            resp_b = await client.post(
                "/api/v1/organizations",
                json={"name": "Org B"},
                headers={"Authorization": f"Bearer {token_b}"}
            )
            assert resp_b.status_code == 201
            org_b_id = resp_b.json()["id"]

            resp = await client.get(
                "/api/v1/employees",
                headers={"Authorization": f"Bearer {token_a}", "x-organization-id": org_b_id}
            )
            assert resp.status_code == 403

            resp = await client.get(
                "/api/v1/employees",
                headers={"Authorization": f"Bearer {token_a}", "x-organization-id": org_a_id}
            )
            assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()

