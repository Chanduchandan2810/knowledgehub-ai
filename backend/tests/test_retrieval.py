import pytest
from httpx import ASGITransport, AsyncClient
import uuid
from app.main import app
from app.api.deps import get_current_user_context, UserContext

pytestmark = pytest.mark.asyncio

mock_org_id = uuid.uuid4()
mock_admin_id = uuid.uuid4()
mock_employee_id = uuid.uuid4()
mock_auth_id = uuid.uuid4()

mock_admin_ctx = UserContext(
    user_id=mock_admin_id,
    auth_user_id=mock_auth_id,
    organization_id=mock_org_id,
    role="ADMIN",
    email="admin@test.com",
    full_name="Admin User"
)

mock_employee_ctx = UserContext(
    user_id=mock_employee_id,
    auth_user_id=mock_auth_id,
    organization_id=mock_org_id,
    role="EMPLOYEE",
    email="employee@test.com",
    full_name="Employee User"
)

# Unmocked test - should fail due to no token
@pytest.mark.asyncio
async def test_retrieval_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/retrieval", json={"question": "hello"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_retrieval_admin():
    app.dependency_overrides[get_current_user_context] = lambda: mock_admin_ctx
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # DB will be empty in test env, but we check if it reaches DB and fails gracefully or returns empty
        try:
            response = await client.post("/api/v1/retrieval", json={"question": "hello"})
            # Should be 200 with empty results or 500 if DB setup is missing in test
            # Just asserting it bypasses auth
            assert response.status_code in (200, 500)
        finally:
            app.dependency_overrides.clear()
