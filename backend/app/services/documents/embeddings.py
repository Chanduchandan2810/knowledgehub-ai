import asyncio
from abc import ABC, abstractmethod
from typing import List
from app.core.config import settings

class EmbeddingService(ABC):
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass

class LocalEmbeddingProvider(EmbeddingService):
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalEmbeddingProvider, cls).__new__(cls)
        return cls._instance

    def _get_model(self):
        if self._model is None:
            # Lazy load the model on first use to speed up app startup
            from sentence_transformers import SentenceTransformer
            # Load the model configured in settings
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    def _encode_sync(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        # encode returns a numpy array, we convert to list of lists of floats
        embeddings = model.encode(texts, batch_size=settings.EMBEDDING_BATCH_SIZE, show_progress_bar=False)
        return embeddings.tolist()

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings asynchronously by offloading the CPU-heavy encoding 
        to a separate thread, keeping the FastAPI event loop unblocked.
        """
        if not texts:
            return []
        return await asyncio.to_thread(self._encode_sync, texts)

def get_embedding_service() -> EmbeddingService:
    if settings.EMBEDDING_PROVIDER.lower() == "local":
        return LocalEmbeddingProvider()
    else:
        raise NotImplementedError(f"Embedding provider '{settings.EMBEDDING_PROVIDER}' is not implemented.")
