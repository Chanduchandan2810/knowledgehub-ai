from pydantic import BaseModel
from typing import List
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

class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievedChunk]
    has_relevant_results: bool
