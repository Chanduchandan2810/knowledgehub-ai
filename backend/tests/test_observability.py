import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch, AsyncMock
from app.services.chat.rag_service import rag_service
from app.api.deps import UserContext
import uuid

@pytest.mark.asyncio
async def test_health_endpoint_structure():
    """Health endpoint returns expected fields without leaking credentials."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code in [200, 503]
        data = res.json()
        assert "status" in data
        assert "database" in data
        assert "ollama" in data
        assert data["status"] in ["ok", "degraded"]
        assert data["database"] in ["ok", "unhealthy"]
        assert data["ollama"] in ["ok", "unhealthy"]
        # Verify no credentials leak
        raw = res.text
        assert "password" not in raw.lower()
        assert "secret" not in raw.lower()
        assert "postgresql://" not in raw
        assert "supabase" not in raw.lower()

@pytest.mark.asyncio
async def test_rag_error_observability(caplog):
    """RAG error emits safe outcome=error log without leaking prompts or exceptions."""
    import logging
    caplog.set_level(logging.INFO)
    
    ctx = UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="EMPLOYEE",
        email="test@example.com",
        full_name="Test"
    )
    
    with patch("app.services.chat.rag_service.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_ret:
        mock_ret.side_effect = Exception("Simulated Failure")
        try:
            await rag_service.generate_answer("What is the refund policy?", ctx, None)
        except Exception:
            pass
            
    found_error_log = False
    for record in caplog.records:
        if "[RAG]" in record.message and "outcome=error" in record.message:
            found_error_log = True
            assert "Simulated Failure" not in record.message
            assert "refund policy" not in record.message
            assert "password" not in record.message.lower()
            assert "jwt" not in record.message.lower()
    
    assert found_error_log

@pytest.mark.asyncio
async def test_rag_stream_error_observability(caplog):
    """RAG-Stream error emits safe outcome=error log without leaking prompts or exceptions."""
    import logging
    caplog.set_level(logging.INFO)
    
    ctx = UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="EMPLOYEE",
        email="test@example.com",
        full_name="Test"
    )
    
    with patch("app.services.chat.rag_service.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_ret:
        mock_ret.side_effect = Exception("Simulated Stream Failure")
        try:
            async for _ in rag_service.generate_answer_stream("What is the refund policy?", ctx, None):
                pass
        except Exception:
            pass
            
    found_error_log = False
    for record in caplog.records:
        if "[RAG-Stream]" in record.message and "outcome=error" in record.message:
            found_error_log = True
            assert "Simulated Stream Failure" not in record.message
            assert "refund policy" not in record.message
            assert "password" not in record.message.lower()
            assert "jwt" not in record.message.lower()
            
    assert found_error_log

@pytest.mark.asyncio
async def test_rag_no_context_observability(caplog):
    """RAG no-context responses are logged safely without leaking queries."""
    import logging
    caplog.set_level(logging.INFO)
    
    ctx = UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="EMPLOYEE",
        email="test@example.com",
        full_name="Test"
    )
    
    mock_response = AsyncMock()
    mock_response.has_relevant_results = False
    mock_response.results = []
    
    with patch("app.services.chat.rag_service.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_ret:
        mock_ret.return_value = mock_response
        result = await rag_service.generate_answer("What is the secret password?", ctx, None)

    found_log = False
    for record in caplog.records:
        if "[RAG]" in record.message and "outcome=no_context" in record.message:
            found_log = True
            assert "secret password" not in record.message
            assert "password" not in record.message.lower()
            
    assert found_log

