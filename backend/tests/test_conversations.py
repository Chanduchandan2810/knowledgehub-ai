import pytest
from httpx import ASGITransport, AsyncClient
import uuid
from app.main import app

pytestmark = pytest.mark.asyncio

async def get_demo_token(client: AsyncClient, role: str) -> str:
    res = await client.post("/api/v1/auth/demo/start", json={"role": role})
    assert res.status_code == 200
    return res.json()["access_token"]

async def test_unauthenticated_access_denied():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/conversations")
        assert resp.status_code == 401

async def test_create_and_list_conversations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create conversation
        res = await client.post(
            "/api/v1/conversations", 
            headers=headers,
            json={"title": "Test Title"}
        )
        assert res.status_code == 201
        conv = res.json()
        assert conv["title"] == "Test Title"
        assert "id" in conv
        conv_id = conv["id"]
        
        # List conversations
        res2 = await client.get("/api/v1/conversations", headers=headers)
        assert res2.status_code == 200
        convs = res2.json()
        assert len(convs) >= 1
        assert any(c["id"] == conv_id for c in convs)

async def test_get_my_conversation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        res = await client.post("/api/v1/conversations", headers=headers, json={"title": "Single Conv"})
        conv_id = res.json()["id"]
        
        res2 = await client.get(f"/api/v1/conversations/{conv_id}", headers=headers)
        assert res2.status_code == 200
        assert res2.json()["id"] == conv_id

async def test_cross_user_isolation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Admin creates conversation
        admin_token = await get_demo_token(client, "ADMIN")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = await client.post("/api/v1/conversations", headers=admin_headers, json={"title": "Admin Secret"})
        conv_id = res.json()["id"]
        
        # Employee attempts to fetch it
        emp_token = await get_demo_token(client, "EMPLOYEE")
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        
        res_fetch = await client.get(f"/api/v1/conversations/{conv_id}", headers=emp_headers)
        assert res_fetch.status_code == 404  # Not found for this user

from unittest.mock import patch, AsyncMock
from app.schemas.chat import RAGResponse
from app.models.message import MessageRole

async def test_send_message_and_multi_turn():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "EMPLOYEE")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create conv
        res = await client.post("/api/v1/conversations", headers=headers, json={"title": "New Conversation"})
        conv_id = res.json()["id"]
        
        # Mock RAG generation so we don't hit LLM
        mock_rag_response = RAGResponse(answer="I am a mocked response.", retrieved_chunks=[])
        
        with patch("app.services.chat.rag_service.rag_service.generate_answer", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_rag_response
            
            # Send message
            msg_res = await client.post(
                f"/api/v1/conversations/{conv_id}/messages",
                headers=headers,
                json={"content": "What is the policy?"}
            )
            assert msg_res.status_code == 200
            data = msg_res.json()
            assert data["user_message"]["content"] == "What is the policy?"
            assert data["assistant_message"]["content"] == "I am a mocked response."
            
            # Get updated title (deterministic first question logic)
            conv_res = await client.get(f"/api/v1/conversations/{conv_id}", headers=headers)
            assert conv_res.json()["title"] == "What is the policy?"
            
            # List messages (should be chronological)
            msgs_res = await client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
            msgs = msgs_res.json()
            assert len(msgs) == 2
            assert msgs[0]["role"] == MessageRole.USER.value
            assert msgs[1]["role"] == MessageRole.ASSISTANT.value

async def test_failed_llm_does_not_save_assistant_message():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        res = await client.post("/api/v1/conversations", headers=headers, json={})
        conv_id = res.json()["id"]
        
        with patch("app.services.chat.rag_service.rag_service.generate_answer", new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = RuntimeError("LLM Offline")
            
            msg_res = await client.post(
                f"/api/v1/conversations/{conv_id}/messages",
                headers=headers,
                json={"content": "Hello?"}
            )
            assert msg_res.status_code == 503
            
            # Check messages - only user message should be saved
            msgs_res = await client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
            msgs = msgs_res.json()
            assert len(msgs) == 1
            assert msgs[0]["role"] == MessageRole.USER.value
            assert msgs[0]["content"] == "Hello?"

async def test_invalid_messages_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        res = await client.post("/api/v1/conversations", headers=headers, json={})
        conv_id = res.json()["id"]
        
        # Empty message
        msg_res = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=headers,
            json={"content": "   "}
        )
        assert msg_res.status_code == 422
        
        # Too large message
        msg_res2 = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=headers,
            json={"content": "a" * 5000}
        )
        assert msg_res2.status_code == 422
