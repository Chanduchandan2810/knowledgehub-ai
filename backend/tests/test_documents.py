import pytest
from httpx import ASGITransport, AsyncClient
import uuid
from app.main import app
from app.api.deps import get_current_user_context, require_admin_role, UserContext
from fastapi import UploadFile

pytestmark = pytest.mark.asyncio

import io

# Mock user contexts
mock_admin_ctx = UserContext(
    user_id=uuid.uuid4(),
    auth_user_id=uuid.uuid4(),
    organization_id=uuid.uuid4(),
    role="ADMIN",
    email="admin@test.com",
    full_name="Admin User"
)

async def override_get_current_user_context():
    return mock_admin_ctx

async def override_require_admin_role():
    return mock_admin_ctx

@pytest.fixture(autouse=True)
def setup_teardown():
    app.dependency_overrides[get_current_user_context] = override_get_current_user_context
    app.dependency_overrides[require_admin_role] = override_require_admin_role
    yield
    app.dependency_overrides.clear()

async def test_employee_forbidden_from_listing():
    # Simulate an employee trying to access admin route
    async def employee_role():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin privileges required")
        
    app.dependency_overrides[require_admin_role] = employee_role
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/documents")
        assert resp.status_code == 403
        assert "Admin privileges required" in resp.json()["detail"]

async def test_employee_cannot_upload():
    async def employee_role():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin privileges required")
        
    app.dependency_overrides[require_admin_role] = employee_role
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 test content"), "application/pdf")}
        resp = await client.post("/api/v1/documents", files=files)
        assert resp.status_code == 403

async def test_invalid_file_type_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.exe", io.BytesIO(b"binary content"), "application/octet-stream")}
        resp = await client.post("/api/v1/documents", files=files)
        assert resp.status_code == 400
        assert "Unsupported file type" in resp.json()["detail"]

async def test_invalid_pdf_magic_bytes_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("fake.pdf", io.BytesIO(b"not a real pdf"), "application/pdf")}
        resp = await client.post("/api/v1/documents", files=files)
        assert resp.status_code == 400
        assert "Invalid PDF file" in resp.json()["detail"]

async def test_empty_file_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
        resp = await client.post("/api/v1/documents", files=files)
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"]
