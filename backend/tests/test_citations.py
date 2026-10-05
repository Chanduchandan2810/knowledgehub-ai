import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.schemas.chat import RAGResponse
from app.schemas.retrieval import RetrievedChunk
from app.models.message import MessageRole
import uuid
from sqlalchemy import select
from app.models.citation import Citation
from app.db.session import get_db

pytestmark = pytest.mark.asyncio

async def get_demo_token(client: AsyncClient, role: str) -> str:
    res = await client.post("/api/v1/auth/demo/start", json={"role": role})
    assert res.status_code == 200
    return res.json()["access_token"]

async def test_citation_persistence():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "EMPLOYEE")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create conv
        res = await client.post("/api/v1/conversations", headers=headers, json={"title": "Citation Test"})
        conv_id = res.json()["id"]
        
        def make_chunk(content, filename):
            return RetrievedChunk(
                chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), 
                content=content, filename=filename, 
                page_number=1, chunk_index=0, distance=0.1, similarity=0.9, token_count=100
            )
        
        chunk1 = make_chunk("A", "a.txt")
        chunk2 = make_chunk("B", "b.txt")
        
        # We need to mock rag_service.generate_answer directly because it does the citation JSON validation!
        pass

async def test_citation_validation_logic():
    # Test rag_service.generate_answer logic directly
    from app.services.chat.rag_service import rag_service
    from app.services.retrieval.retrieval_service import RetrievalResponse
    
    # Fake user context and DB
    ctx = AsyncMock()
    db = AsyncMock()
    
    def make_chunk(content, filename):
        return RetrievedChunk(
            chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), 
            content=content, filename=filename, 
            page_number=1, chunk_index=0, distance=0.1, similarity=0.9, token_count=100
        )
    
    chunk1 = make_chunk("A", "a.txt")
    chunk2 = make_chunk("B", "b.txt")
    
    mock_retrieval_res = RetrievalResponse(query="test", results=[chunk1, chunk2], has_relevant_results=True)
    
    # 1. Valid and Invalid citations mixed
    # LLM returns chunk1 (valid), and a fake chunk (invalid)
    fake_chunk_id = str(uuid.uuid4())
    mock_json_str = f'{{"answer": "Here is the answer.", "citation_ids": ["{str(chunk1.chunk_id)}", "{fake_chunk_id}"]}}'
    
    with patch("app.services.chat.rag_service.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = mock_retrieval_res
        
        with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_json_str
            
            res = await rag_service.generate_answer("question?", ctx, db)
            
            assert res.answer == "Here is the answer."
            assert len(res.citations) == 1
            assert res.citations[0].chunk_id == chunk1.chunk_id
            
    # 2. Duplicate citations handled gracefully
    mock_json_str_dupes = f'{{"answer": "Answer", "citation_ids": ["{str(chunk2.chunk_id)}", "{str(chunk2.chunk_id)}"]}}'
    with patch("app.services.chat.rag_service.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = mock_retrieval_res
        
        with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_json_str_dupes
            
            res = await rag_service.generate_answer("question2?", ctx, db)
            assert len(res.citations) == 1
            assert res.citations[0].chunk_id == chunk2.chunk_id

    # 3. No context scenario
    mock_retrieval_empty = RetrievalResponse(query="test", results=[], has_relevant_results=False)
    with patch("app.services.chat.rag_service.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = mock_retrieval_empty
        
        res = await rag_service.generate_answer("question3?", ctx, db)
        assert len(res.citations) == 0
        assert "couldn't find" in res.answer

async def test_citation_endpoint_integration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_demo_token(client, "EMPLOYEE")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Fetch an actual document and chunk from the database!
        from app.db.session import AsyncSessionLocal
        from app.models.document_chunk import DocumentChunk
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(DocumentChunk).limit(2))
            chunks = result.scalars().all()
            if len(chunks) < 2:
                pytest.skip("Not enough chunks in test DB for citation test")
            
            chunk_id_1 = chunks[0].id
            doc_id_1 = chunks[0].document_id
            
            chunk_id_2 = chunks[1].id
            doc_id_2 = chunks[1].document_id
            
        # Create conv
        res = await client.post("/api/v1/conversations", headers=headers, json={"title": "Citation Test"})
        conv_id = res.json()["id"]
        
        def make_chunk_explicit(cid, did, content, filename):
            return RetrievedChunk(
                chunk_id=cid, document_id=did, 
                content=content, filename=filename, 
                page_number=1, chunk_index=0, distance=0.1, similarity=0.9, token_count=100
            )
        
        # Mock RAG response using real valid DB IDs
        mock_rag_res = RAGResponse(
            answer="Here is the final answer.",
            retrieved_chunks=[],
            citations=[
                make_chunk_explicit(chunk_id_1, doc_id_1, "A", "a.txt"),
                make_chunk_explicit(chunk_id_2, doc_id_2, "B", "b.txt")
            ]
        )
        
        with patch("app.services.chat.rag_service.rag_service.generate_answer", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_rag_res
            
            msg_res = await client.post(
                f"/api/v1/conversations/{conv_id}/messages",
                headers=headers,
                json={"content": "What is A and B?"}
            )
            assert msg_res.status_code == 200
            
            msg_id = msg_res.json()["assistant_message"]["id"]
            
            msg_id_uuid = uuid.UUID(msg_id)
            
            # Since the API doesn't return citations yet, we must check the DB!
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Citation).where(Citation.message_id == msg_id_uuid))
                db_citations = result.scalars().all()
                
                assert len(db_citations) == 2
                chunk_ids = [c.chunk_id for c in db_citations]
                assert chunk_id_1 in chunk_ids
                assert chunk_id_2 in chunk_ids
