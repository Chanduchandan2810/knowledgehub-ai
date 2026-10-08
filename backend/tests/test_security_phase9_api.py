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
        res_a = await client.post(f"/api/v1/documents/{doc_a_id}/process", headers=headers)
        assert res_a.status_code == 200

@pytest.mark.asyncio
async def test_idor_document_deletion_rejected():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}

        # Upload Doc A for Org A
        files = {"file": ("org_a_doc.txt", io.BytesIO(b"Content A"), "text/plain")}
        res_upload = await client.post("/api/v1/documents", headers=headers, files=files)
        assert res_upload.status_code == 201
        doc_a_id = res_upload.json()["id"]

        # Create Org B and Doc B
        from app.db.session import AsyncSessionLocal
        from app.models.organization import Organization
        from app.models.document import Document, AccessScope, DocumentStatus

        org_b_id = uuid.uuid4()
        doc_b_id = uuid.uuid4()

        async with AsyncSessionLocal() as session:
            session.add(Organization(id=org_b_id, name="Org B"))
            await session.commit()

            session.add(Document(
                id=doc_b_id,
                organization_id=org_b_id,
                filename="org_b_doc.txt",
                storage_path="org_b/doc.txt",
                mime_type="text/plain",
                file_size=10,
                status=DocumentStatus.UPLOADED.value,
                access_scope=AccessScope.ORGANIZATION.value
            ))
            await session.commit()

        # Admin A attempts to delete Doc B
        res_delete_b = await client.delete(f"/api/v1/documents/{doc_b_id}", headers=headers)
        assert res_delete_b.status_code == 404

        # Admin A deletes Doc A
        res_delete_a = await client.delete(f"/api/v1/documents/{doc_a_id}", headers=headers)
        assert res_delete_a.status_code == 204

@pytest.mark.asyncio
async def test_employee_creation_no_hardcoded_password():
    from app.api.deps import require_admin_role, get_current_user_context, UserContext
    from unittest.mock import AsyncMock, patch, MagicMock
    import uuid

    # Mock admin context to bypass DB auth lookups
    mock_ctx = UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        email="admin@test.com",
        full_name="Admin",
        role="ADMIN"
    )

    async def override_ctx():
        return mock_ctx

    app.dependency_overrides[get_current_user_context] = override_ctx
    app.dependency_overrides[require_admin_role] = override_ctx

    try:
        async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:

            with patch("app.api.v1.employees.create_client") as mock_create_client, \
                 patch("sqlalchemy.ext.asyncio.AsyncSession.flush", new_callable=AsyncMock), \
                 patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new_callable=AsyncMock), \
                 patch("sqlalchemy.ext.asyncio.AsyncSession.refresh", new_callable=AsyncMock), \
                 patch("sqlalchemy.ext.asyncio.AsyncSession.execute", new_callable=AsyncMock) as mock_execute:

                # Mock execute so the "already exists" check returns None, and doc query returns empty
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_docs_result = MagicMock()
                mock_docs_result.scalars().all.return_value = []
                mock_execute.side_effect = [mock_result, mock_docs_result]

                mock_supabase = mock_create_client.return_value
                mock_create_user = mock_supabase.auth.admin.create_user

                class MockUser:
                    id = str(uuid.uuid4())
                class MockRes:
                    user = MockUser()
                mock_create_user.return_value = MockRes()

                def mock_add(obj, *args, **kwargs):
                    if hasattr(obj, 'id') and getattr(obj, 'id', None) is None:
                        obj.id = uuid.uuid4()

                with patch("sqlalchemy.ext.asyncio.AsyncSession.add", side_effect=mock_add):
                    res = await client.post("/api/v1/employees", json={"email": f"securetest_{uuid.uuid4()}@example.com", "full_name": "Test Emp"})

                assert res.status_code == 200, res.text

                call_args = mock_create_user.call_args[0][0]
                assert "password" in call_args
                assert call_args["password"] != "123456"
                assert len(call_args["password"]) >= 32

                # Verify the response payload includes the temporary password
                data = res.json()
                assert "temporary_password" in data
                assert data["temporary_password"] == call_args["password"]
                assert data["temporary_password"] != "123456"

                # Now test GET doesn't expose it
                mock_emp = MagicMock()
                mock_emp.id = uuid.uuid4()
                mock_emp.auth_user_id = uuid.uuid4()
                mock_emp.email = data["email"]
                mock_emp.full_name = "Test Emp"
                mock_emp.created_at = None

                mock_get_result = MagicMock()
                mock_get_result.scalars().all.return_value = [mock_emp]
                mock_execute.side_effect = [mock_get_result]

                res_get = await client.get("/api/v1/employees")
                assert res_get.status_code == 200, res_get.text
                get_data = res_get.json()

                for emp in get_data:
                    if emp["email"] == data["email"]:
                        assert emp.get("temporary_password") is None
                        break
    finally:
        app.dependency_overrides.clear()

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
