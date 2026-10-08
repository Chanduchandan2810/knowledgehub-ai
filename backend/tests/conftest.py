import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
import httpx

@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    from app.core import security
    import app.main
    import supabase

    mock_client = MagicMock()

    def fake_get_user(token):
        if token == "INVALID_TOKEN" or token.endswith("aaaaa"):
            # Simulate supabase throwing an exception for invalid tokens
            raise Exception("Invalid JWT")

        resp = MagicMock()
        resp.user = MagicMock()
        if "admin" in token.lower() or "admin" in token:
            resp.user.id = "c402535c-e5dd-4d7e-8dbe-b4d5d4921ce9"
            resp.user.email = "admin@demo.knowledgehub.local"
        else:
            resp.user.id = "d180181a-7922-40a2-a842-a0b5ddbb35b4"
            resp.user.email = "employee@demo.knowledgehub.local"
        resp.user.user_metadata = {}
        return resp

    def fake_sign_in(credentials):
        email = credentials.get("email", "")
        if "invalid" in email.lower():
            raise Exception("Invalid login")
        resp = MagicMock()
        resp.session.access_token = "admin_token" if "admin" in email else "employee_token"
        resp.session.refresh_token = "fake-refresh"
        resp.session.expires_in = 3600
        return resp

    mock_client.auth.get_user = fake_get_user
    mock_client.auth.sign_in_with_password = fake_sign_in

    def fake_list_users():
        u1 = MagicMock()
        u1.email = "admin@demo.knowledgehub.local"
        u1.id = "c402535c-e5dd-4d7e-8dbe-b4d5d4921ce9"
        u2 = MagicMock()
        u2.email = "employee@demo.knowledgehub.local"
        u2.id = "d180181a-7922-40a2-a842-a0b5ddbb35b4"
        return [u1, u2]

    mock_client.auth.admin.list_users = fake_list_users

    def fake_create_client(*args, **kwargs):
        return mock_client

    monkeypatch.setattr(security, "supabase", mock_client)
    monkeypatch.setattr(supabase, "create_client", fake_create_client)
    if hasattr(app.main, "create_client"):
        monkeypatch.setattr(app.main, "create_client", fake_create_client)
    import app.api.v1.auth as auth
    if hasattr(auth, "supabase"):
        monkeypatch.setattr(auth, "supabase", mock_client)

    return mock_client

import os
import pytest_asyncio
from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings

@pytest_asyncio.fixture(autouse=True, scope="session")
async def seed_demo_data():
    db_url = str(settings.DATABASE_URL) if settings.DATABASE_URL else ""
    # Safety: Do not seed automatically against real remote Supabase DB instances
    if "supabase.com" in db_url or "supabase.co" in db_url:
        return

    if not engine:
        return

    admin_auth_id = "c402535c-e5dd-4d7e-8dbe-b4d5d4921ce9"
    employee_auth_id = "d180181a-7922-40a2-a842-a0b5ddbb35b4"
    org_id = str(settings.DEMO_ORG_ID)
    admin_id = str(settings.DEMO_ADMIN_ID)
    emp_id = str(settings.DEMO_EMPLOYEE_ID)

    async with engine.begin() as conn:
        # Seed auth schema just in case tests run locally without CI initialization
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth;"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS auth.users (id UUID PRIMARY KEY);"))

        # 1. auth.users
        await conn.execute(text(f"INSERT INTO auth.users (id) VALUES ('{admin_auth_id}') ON CONFLICT DO NOTHING;"))
        await conn.execute(text(f"INSERT INTO auth.users (id) VALUES ('{employee_auth_id}') ON CONFLICT DO NOTHING;"))

        # 2. organizations
        await conn.execute(text(f"INSERT INTO organizations (id, name) VALUES ('{org_id}', 'Demo Organization') ON CONFLICT DO NOTHING;"))

        # 3. admins
        await conn.execute(text(f"INSERT INTO admins (id, auth_user_id, organization_id, full_name, email) VALUES ('{admin_id}', '{admin_auth_id}', '{org_id}', 'Demo Admin', 'admin@demo.knowledgehub.local') ON CONFLICT DO NOTHING;"))

        # 4. employees
        await conn.execute(text(f"INSERT INTO employees (id, auth_user_id, organization_id, full_name, email) VALUES ('{emp_id}', '{employee_auth_id}', '{org_id}', 'Demo Employee', 'employee@demo.knowledgehub.local') ON CONFLICT DO NOTHING;"))

from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def mock_storage(monkeypatch):
    mock_upload = AsyncMock()
    async def fake_upload(file_bytes, storage_path, mime_type):
        return storage_path
    mock_upload.side_effect = fake_upload

    mock_delete = AsyncMock()

    # Patch where the functions are imported and used
    monkeypatch.setattr("app.api.v1.documents.upload_document_to_storage", mock_upload)
    monkeypatch.setattr("app.api.v1.documents.delete_document_from_storage", mock_delete)

    return mock_upload, mock_delete
