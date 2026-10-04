import pytest
from httpx import ASGITransport, AsyncClient
import uuid
from app.main import app

pytestmark = pytest.mark.asyncio

async def test_demo_unauthenticated_on_normal_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/employees")
        assert response.status_code == 401

async def test_demo_admin_session_works():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Start demo
        start_res = await client.post("/api/v1/auth/demo/start", json={"role": "ADMIN"})
        assert start_res.status_code == 200
        token = start_res.json()["access_token"]

        # Test endpoint
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@demo.knowledgehub.local"

async def test_demo_employee_session_works():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_res = await client.post("/api/v1/auth/demo/start", json={"role": "EMPLOYEE"})
        assert start_res.status_code == 200
        token = start_res.json()["access_token"]

        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "employee@demo.knowledgehub.local"

async def test_demo_employee_denied_admin_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_res = await client.post("/api/v1/auth/demo/start", json={"role": "EMPLOYEE"})
        token = start_res.json()["access_token"]

        response = await client.get("/api/v1/employees", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

async def test_modified_demo_token_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_res = await client.post("/api/v1/auth/demo/start", json={"role": "EMPLOYEE"})
        token = start_res.json()["access_token"]

        # Tamper with token
        tampered_token = token[:-5] + "aaaaa"
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
        assert response.status_code == 401
async def test_demo_end_to_end_chat():
    from unittest.mock import patch
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_res = await client.post("/api/v1/auth/demo/start", json={"role": "EMPLOYEE"})
        assert start_res.status_code == 200
        token = start_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        conv_res = await client.post("/api/v1/conversations", headers=headers, json={"title": "Demo Test"})
        assert conv_res.status_code == 201
        conv_id = conv_res.json()["id"]

        async def mock_generate_answer_stream(content, ctx, db):
            yield {"type": "token", "text": "Mock"}
            yield {"type": "token", "text": " Demo"}
            yield {"type": "citations", "citations": []}

        with patch("app.api.v1.conversations.rag_service.generate_answer_stream", side_effect=mock_generate_answer_stream):
            async with client.stream("POST", f"/api/v1/conversations/{conv_id}/messages/stream", headers=headers, json={"content": "Streaming demo test?"}) as stream_res:
                assert stream_res.status_code == 200
                events = []
                async for line in stream_res.aiter_lines():
                    if line.startswith("event: "):
                        events.append(line.split("event: ")[1])

                assert "start" in events
                assert "token" in events
                assert "done" in events

        msgs_res = await client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
        assert msgs_res.status_code == 200
        assert len(msgs_res.json()) == 2
