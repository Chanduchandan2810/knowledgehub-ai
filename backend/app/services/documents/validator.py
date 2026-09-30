from typing import List
from app.core.config import settings

def validate_embeddings(embeddings: List[List[float]]) -> None:
    expected_dim = settings.EMBEDDING_DIMENSIONS
    
    for idx, emb in enumerate(embeddings):
        if len(emb) != expected_dim:
            raise ValueError(f"Vector dimension mismatch at index {idx}. Expected {expected_dim}, got {len(emb)}")
