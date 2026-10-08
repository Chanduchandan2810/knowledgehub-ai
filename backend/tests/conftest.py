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
