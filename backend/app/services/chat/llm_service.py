import httpx
import logging
from app.core.config import settings
import traceback

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    async def check_health(self) -> dict:
        """
        Check if Ollama is available and if the required model is loaded.
        Returns a dict with 'status' and 'details'.
        """
        try:
            # 1. Check if Ollama is reachable
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                
                if res.status_code != 200:
                    return {
                        "status": "unhealthy",
                        "details": f"Ollama returned status {res.status_code}"
                    }
                
                # 2. Check if the required model is available
                data = res.json()
                models = data.get("models", [])
                
                model_names = [m.get("name") for m in models]
                
                # Try exact match, or check if base model matches
                if self.model not in model_names and f"{self.model}:latest" not in model_names:
                    return {
                        "status": "unhealthy",
                        "details": f"Model '{self.model}' not found in Ollama. Available: {model_names}"
                    }
                
                return {
                    "status": "healthy",
                    "details": f"Ollama is reachable and '{self.model}' is available."
                }
                
        except httpx.RequestError as e:
            return {
                "status": "unhealthy",
                "details": f"Could not connect to Ollama at {self.base_url}: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": f"Unexpected error during health check: {str(e)}"
            }

llm_service = LLMService()
