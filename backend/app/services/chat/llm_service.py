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

    async def generate_chat(self, system_prompt: str, user_prompt: str, response_format: str | None = None) -> str:
        """
        Generate a response using the native Ollama HTTP API.
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Keep it grounded
                        "top_p": 0.9,
                    }
                }
                
                if response_format:
                    payload["format"] = response_format
                
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                
                if res.status_code != 200:
                    logger.error(f"Ollama API returned status {res.status_code}: {res.text}")
                    raise RuntimeError("Failed to generate response from LLM service.")
                
                data = res.json()
                message = data.get("message", {})
                content = message.get("content", "")
                
                return content
                
        except httpx.RequestError as e:
            logger.error(f"Connection error while calling Ollama: {str(e)}")
            raise RuntimeError("LLM service is currently unreachable.")
        except Exception as e:
            logger.error(f"Unexpected error during LLM generation: {str(e)}")
            raise RuntimeError("An unexpected error occurred during generation.")

llm_service = LLMService()
