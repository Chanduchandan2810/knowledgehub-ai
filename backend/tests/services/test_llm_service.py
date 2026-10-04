import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.chat.llm_service import LLMService
from app.core.config import settings
import httpx

@pytest.fixture
def llm_service():
    return LLMService()

def test_ollama_config_exists():
    assert hasattr(settings, "OLLAMA_BASE_URL")
    assert hasattr(settings, "OLLAMA_MODEL")
    assert settings.OLLAMA_BASE_URL == "http://localhost:11434"

@pytest.mark.asyncio
async def test_check_health_healthy(llm_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [{"name": settings.OLLAMA_MODEL}]
    }
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("httpx.AsyncClient.__aenter__", return_value=mock_client):
        result = await llm_service.check_health()
        assert result["status"] == "healthy"
        assert settings.OLLAMA_MODEL in result["details"]

@pytest.mark.asyncio
async def test_check_health_model_missing(llm_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [{"name": "some_other_model:latest"}]
    }
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("httpx.AsyncClient.__aenter__", return_value=mock_client):
        result = await llm_service.check_health()
        assert result["status"] == "unhealthy"
        assert "not found" in result["details"]

@pytest.mark.asyncio
async def test_check_health_unreachable(llm_service):
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.RequestError("Connection failed")
    
    with patch("httpx.AsyncClient.__aenter__", return_value=mock_client):
        result = await llm_service.check_health()
        assert result["status"] == "unhealthy"
        assert "Could not connect" in result["details"]
