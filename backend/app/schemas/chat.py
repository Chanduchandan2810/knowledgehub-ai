from pydantic import BaseModel
from typing import List
from app.schemas.retrieval import RetrievedChunk

class RAGResponse(BaseModel):
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    citations: List[RetrievedChunk] = []
