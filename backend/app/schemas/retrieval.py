from pydantic import BaseModel
from typing import List, Optional
import uuid

class RetrievalRequest(BaseModel):
    question: str

class RetrievedChunk(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    page_number: int | None
    chunk_index: int
    content: str
    distance: float
    similarity: float
    token_count: int
    # Phase 7 Hybrid Search scoring (internal, not exposed to frontend)
    vector_score: Optional[float] = None
    keyword_score: Optional[float] = None
    hybrid_score: Optional[float] = None
    retrieval_method: Optional[str] = None  # 'vector', 'keyword', or 'hybrid'

class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievedChunk]
    has_relevant_results: bool
