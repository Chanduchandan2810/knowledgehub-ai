import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
async def get_demo_token(client: AsyncClient, role: str) -> str:
    res = await client.post("/api/v1/auth/demo/start", json={"role": role})
    assert res.status_code == 200
    return res.json()["access_token"]

from unittest.mock import patch, AsyncMock
import uuid
import io

@pytest.mark.asyncio
async def test_idor_document_reprocessing_rejected():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        # We will create an Org B context and upload a document.
        # But instead of messy overrides, let's just insert via AsyncSessionLocal but do it properly one by one!
        
        # Actually, let's just use the demo token to upload a document for Org A.
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload a valid txt file to Org A
        files = {"file": ("org_a_doc.txt", io.BytesIO(b"Valid text content for org A."), "text/plain")}
        res_upload = await client.post("/api/v1/documents", headers=headers, files=files)
        assert res_upload.status_code == 201
        doc_a_id = res_upload.json()["id"]
        
        # Now insert Org B and Doc B cleanly using a separate session
        from app.db.session import AsyncSessionLocal
        from app.models.organization import Organization
        from app.models.document import Document, DocumentStatus, AccessScope
        
        org_b_id = uuid.uuid4()
        doc_b_id = uuid.uuid4()
        
        async with AsyncSessionLocal() as session:
            org_b = Organization(id=org_b_id, name="Org B")
            session.add(org_b)
            await session.commit()
            
            doc_b = Document(
                id=doc_b_id,
                organization_id=org_b_id,
                filename="org_b_doc.txt",
                storage_path="org_b/doc.txt",
                mime_type="text/plain",
                file_size=100,
                status=DocumentStatus.FAILED.value,
                access_scope=AccessScope.ORGANIZATION.value
            )
            session.add(doc_b)
            await session.commit()
            
        # Try IDOR on Doc B
        res_b = await client.post(f"/api/v1/documents/{doc_b_id}/process", headers=headers)
        assert res_b.status_code == 404
        assert "Document not found" in res_b.json()["detail"]
        
        # Try self on Doc A
        # Since we just uploaded it, it's UPLOADED, not FAILED/PROCESSED, so process endpoint will reject it with 400.
        # Let's mock it to FAILED or just accept the 400 as proof it found the document.
        res_a = await client.post(f"/api/v1/documents/{doc_a_id}/process", headers=headers)
        assert res_a.status_code == 200

@pytest.mark.asyncio
async def test_employee_creation_no_hardcoded_password():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        with patch("app.api.v1.employees.create_client") as mock_create_client:
            mock_supabase = mock_create_client.return_value
            mock_create_user = mock_supabase.auth.admin.create_user
            
            class MockUser:
                id = str(uuid.uuid4())
            class MockRes:
                user = MockUser()
            mock_create_user.return_value = MockRes()
            
            res = await client.post("/api/v1/employees", headers=headers, json={"email": "securetest@example.com", "full_name": "Test Emp"})
            
            call_args = mock_create_user.call_args[0][0]
            assert "password" in call_args
            assert call_args["password"] != "123456"
            assert len(call_args["password"]) >= 32

@pytest.mark.asyncio
async def test_rate_limiter_demo_abuse():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        random_doc_id = uuid.uuid4()
        
        for i in range(5):
            res = await client.post(f"/api/v1/documents/{random_doc_id}/process", headers=headers)
            assert res.status_code == 404
            
        res6 = await client.post(f"/api/v1/documents/{random_doc_id}/process", headers=headers)
        assert res6.status_code == 429
        assert "Rate limit exceeded" in res6.json()["detail"]
