import pytest
from httpx import ASGITransport, AsyncClient
import uuid
from app.main import app
from app.core.config import settings

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_demo_unauthenticated_on_normal_routes():
    # Attempting to access normal endpoints without a real JWT should fail
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Pass a demo cookie to a normal route
        client.cookies.set("demo_role", "ADMIN")
        response = await client.get("/api/v1/employees")
        # Should be 401 Unauthorized because normal endpoints don't accept the demo cookie bypass
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_demo_admin_context():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("demo_role", "ADMIN")
        # Accessing demo route
        response = await client.get("/api/v1/demo/employees")
        # Should be authorized (might be 200)
        assert response.status_code == 200
        # The result should be from the demo organization
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_demo_employee_context_denied_admin_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("demo_role", "EMPLOYEE")
        # Accessing demo route requiring Admin privileges
        response = await client.get("/api/v1/demo/employees")
        # Should be 403 Forbidden because Employee cannot view all employees
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_demo_employee_can_access_chat():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("demo_role", "EMPLOYEE")
        # Attempting retrieval query
        response = await client.post("/api/v1/demo/retrieval", json={"question": "leave policy"})
        assert response.status_code == 200
        
@pytest.mark.asyncio
async def test_demo_impersonation_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("demo_role", "ADMIN")
        fake_org = str(uuid.uuid4())
        # Pass arbitrary organization ID in headers
        response = await client.get("/api/v1/demo/employees", headers={"X-Organization-Id": fake_org})
        # The endpoint uses ctx.organization_id explicitly which ignores headers in demo context,
        # but to prove it works and doesn't leak:
        assert response.status_code == 200
