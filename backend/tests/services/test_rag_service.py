import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.schemas.chat import RAGResponse
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.services.chat.rag_service import rag_service, NO_CONTEXT_MESSAGE, SYSTEM_PROMPT, ContextBuilder
from app.api.deps import UserContext

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_ctx():
    return UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="EMPLOYEE",
        email="test@example.com",
        full_name="Test User"
    )

@pytest.fixture
def mock_retrieved_chunk():
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename="test_doc.pdf",
        page_number=1,
        chunk_index=0,
        content="Employees receive 20 days of annual leave.",
        distance=0.1,
        similarity=0.9,
        token_count=10
    )

async def test_no_context_returns_fallback_without_calling_llm(mock_ctx):
    empty_retrieval = RetrievalResponse(
        query="test",
        results=[],
        has_relevant_results=False
    )
    
    with patch("app.services.chat.agent_tools.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = empty_retrieval
        
        with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '{"tool": "standard_rag"}'
            
            response = await rag_service.generate_answer("How many leave days?", mock_ctx, AsyncMock())
            
            assert response.answer == NO_CONTEXT_MESSAGE
            assert len(response.retrieved_chunks) == 0
            assert mock_generate.call_count == 1 # Only called for router, second call is skipped because no_context

async def test_context_builder_formats_correctly(mock_retrieved_chunk):
    context, alias_map = ContextBuilder.build_context([mock_retrieved_chunk])
    
    assert "[SOURCE]" in context
    assert "[/SOURCE]" in context
    assert "Citation Alias: [DOC-1]" in context
    assert "test_doc.pdf" in context
    assert "Page: 1" in context
    assert "Employees receive 20 days of annual leave." in context
    assert alias_map["[DOC-1]"] == str(mock_retrieved_chunk.chunk_id)
    
    # Verify NO vectors or embeddings are in the context
    assert "0.1" not in context  # Distance should not be in the prompt
    assert "0.9" not in context  # Similarity should not be in the prompt

async def test_generation_sends_correct_prompts(mock_ctx, mock_retrieved_chunk):
    retrieval = RetrievalResponse(
        query="test",
        results=[mock_retrieved_chunk],
        has_relevant_results=True
    )
    
    with patch("app.services.chat.agent_tools.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = retrieval
        
        with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = ['{"tool": "standard_rag"}', "Employees receive 20 days."]
            
            response = await rag_service.generate_answer("How many leave days?", mock_ctx, AsyncMock())
            
            # Assert correct response
            assert response.answer == "Employees receive 20 days."
            assert len(response.retrieved_chunks) == 1
            assert response.retrieved_chunks[0] == mock_retrieved_chunk
            
            # Assert generate_chat was called with correct parameters
            assert mock_generate.call_count == 2
            kwargs = mock_generate.call_args_list[-1].kwargs
            
            assert kwargs["system_prompt"] == SYSTEM_PROMPT
            
            user_prompt = kwargs["user_prompt"]
            assert "How many leave days?" in user_prompt
            assert "Employees receive 20 days of annual leave." in user_prompt
            
            # Verify prompt injection defense logic (separation of context)
            assert "QUESTION:" in user_prompt
            assert "CONTEXT:" in user_prompt

async def test_multiple_chunks_ordering(mock_ctx):
    chunk1 = RetrievedChunk(
        chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), filename="doc1.pdf",
        page_number=1, chunk_index=0, content="First fact.", distance=0.1, similarity=0.9, token_count=5
    )
    chunk2 = RetrievedChunk(
        chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), filename="doc2.pdf",
        page_number=2, chunk_index=1, content="Second fact.", distance=0.2, similarity=0.8, token_count=5
    )
    
    context, alias_map = ContextBuilder.build_context([chunk1, chunk2])
    
    idx1 = context.find("First fact.")
    idx2 = context.find("Second fact.")
    assert idx1 != -1
    assert idx2 != -1
    assert idx1 < idx2
    assert alias_map["[DOC-1]"] == str(chunk1.chunk_id)
    assert alias_map["[DOC-2]"] == str(chunk2.chunk_id)

async def test_llm_failure_handled_cleanly(mock_ctx, mock_retrieved_chunk):
    retrieval = RetrievalResponse(
        query="test",
        results=[mock_retrieved_chunk],
        has_relevant_results=True
    )
    
    with patch("app.services.chat.agent_tools.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = retrieval
        
        with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = RuntimeError("LLM service is currently unreachable.")
            
            with pytest.raises(RuntimeError, match="LLM service is currently unreachable."):
                await rag_service.generate_answer("Test?", mock_ctx, AsyncMock())

async def test_security_authorization_isolation():
    """
    Demonstrates that the RAG service correctly reuses the Phase 5 retrieval 
    which applies strict tenant and permission isolation.
    We test this by inspecting the actual SQLAlchemy query compiled by retrieve_chunks.
    """
    from app.services.retrieval.retrieval_service import retrieve_chunks
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # 1. Test Organization A vs Organization B
    org_a_id = uuid.uuid4()
    ctx_a = UserContext(
        user_id=uuid.uuid4(), auth_user_id=uuid.uuid4(), organization_id=org_a_id,
        role="ADMIN", email="a@test.com", full_name="A"
    )
    
    mock_result = MagicMock()
    mock_result.all.return_value = []
    
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = mock_result
    
    # We patch get_embedding_service to avoid local LLM initialization during test
    with patch("app.services.retrieval.retrieval_service.get_embedding_service") as mock_embed:
        mock_embed.return_value.generate_embeddings = AsyncMock(return_value=[[0.0] * 384])
        
        # We just want to capture the query passed to db.execute
        await retrieve_chunks("test query", ctx_a, mock_db)
        
        # Get the query object from the mock call
        call_args = mock_db.execute.call_args
        query_obj = call_args[0][0]
        
        compiled_query = str(query_obj.compile(compile_kwargs={"literal_binds": True}))
        
        # Verify Organization A isolation is present
        assert "document_chunks.organization_id =" in compiled_query
        assert "documents.organization_id =" in compiled_query
        assert org_a_id.hex in compiled_query
        
        # Verify ADMIN permission check
        assert "document_permissions.admin_id =" in compiled_query
        
    # 2. Test Employee permissions
    emp_id = uuid.uuid4()
    ctx_emp = UserContext(
        user_id=emp_id, auth_user_id=uuid.uuid4(), organization_id=org_a_id,
        role="EMPLOYEE", email="e@test.com", full_name="E"
    )
    
    with patch("app.services.retrieval.retrieval_service.get_embedding_service") as mock_embed:
        mock_embed.return_value.generate_embeddings = AsyncMock(return_value=[[0.0] * 384])
        
        await retrieve_chunks("test query", ctx_emp, mock_db)
        
        call_args = mock_db.execute.call_args
        query_obj = call_args[0][0]
        compiled_query = str(query_obj.compile(compile_kwargs={"literal_binds": True}))
        
        # Verify EMPLOYEE permission check
        assert "document_permissions.employee_id =" in compiled_query
        assert emp_id.hex in compiled_query
