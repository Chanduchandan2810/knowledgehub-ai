import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.security import verify_token
import uuid
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security

pytestmark = pytest.mark.asyncio

async def test_employee_creation():
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import text
    from unittest.mock import patch, MagicMock

    user1_id = str(uuid.uuid4())

    # Pre-seed auth.users to satisfy FK constraint
    async with AsyncSessionLocal() as db:
        await db.execute(text(f"INSERT INTO auth.users (id) VALUES ('{user1_id}') ON CONFLICT DO NOTHING"))
        await db.commit()

    token1 = "admin_token1"
    headers1 = {"Authorization": f"Bearer {token1}"}

    def override_verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
        if credentials.credentials == "admin_token1":
            return {"sub": user1_id, "email": f"admin1_{user1_id}@test.com", "user_metadata": {"full_name": "Admin One"}}
        raise HTTPException(status_code=401, detail="Invalid token")

    app.dependency_overrides[verify_token] = override_verify_token

    mock_supabase = MagicMock()
    mock_user_res = MagicMock()
    new_employee_auth_id = str(uuid.uuid4())
    mock_user_res.user.id = new_employee_auth_id
    mock_supabase.auth.admin.create_user.return_value = mock_user_res

    # We also need to seed the newly created employee auth id so the DB insertion of the employee succeeds
    async with AsyncSessionLocal() as db:
        await db.execute(text(f"INSERT INTO auth.users (id) VALUES ('{new_employee_auth_id}') ON CONFLICT DO NOTHING"))
        await db.commit()

    try:
        with patch("app.api.v1.employees.create_client", return_value=mock_supabase):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/v1/organizations",
                    json={"name": "Org 1"},
                    headers=headers1
                )
                assert resp.status_code == 201
                org_id = resp.json()["id"]

                # Admin creates employee
                headers1_org = {"Authorization": f"Bearer {token1}", "x-organization-id": org_id}
                resp = await client.post(
                    "/api/v1/employees",
                    json={"email": f"employee_{uuid.uuid4()}@test.com", "full_name": "Employee One"},
                    headers=headers1_org
                )

                assert resp.status_code == 200
                data = resp.json()
                assert data["role"] == "EMPLOYEE"
                assert data["auth_user_id"] == new_employee_auth_id
    finally:
        app.dependency_overrides.clear()
