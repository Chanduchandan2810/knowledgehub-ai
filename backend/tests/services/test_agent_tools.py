import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.api.deps import UserContext
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.services.chat.agent_tools import tool_standard_rag, tool_summarize_document, tool_compare_documents
from app.services.chat.rag_service import rag_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_ctx_employee():
    return UserContext(user_id=uuid.uuid4(), auth_user_id=uuid.uuid4(), organization_id=uuid.uuid4(), role="EMPLOYEE", email="emp@example.com", full_name="Employee User")

@pytest.fixture
def mock_ctx_admin():
    return UserContext(user_id=uuid.uuid4(), auth_user_id=uuid.uuid4(), organization_id=uuid.uuid4(), role="ADMIN", email="admin@example.com", full_name="Admin User")

@pytest.fixture
def fake_chunk():
    return RetrievedChunk(
        chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), filename="Test.pdf",
        page_number=1, chunk_index=0, content="x", distance=0.1, similarity=0.9, token_count=10
    )

async def test_standard_rag_calls_hybrid(mock_ctx_employee):
    db = AsyncMock(spec=AsyncSession)
    with patch("app.services.chat.agent_tools.hybrid_retrieve_chunks", new_callable=AsyncMock) as mock_hybrid:
        mock_hybrid.return_value = RetrievalResponse(query="test", results=[], has_relevant_results=False)
        res = await tool_standard_rag({"query": "my search"}, mock_ctx_employee, db)
        mock_hybrid.assert_called_once_with("my search", mock_ctx_employee, db)
        assert res.query == "test"

async def test_summarize_authorized_document(mock_ctx_employee):
    db = AsyncMock(spec=AsyncSession)
    doc_mock = MagicMock()
    doc_mock.id = uuid.uuid4()
    doc_mock.filename = "Policy.pdf"
    
    mock_result_doc = MagicMock()
    mock_result_doc.first.return_value = doc_mock
    
    mock_chunk = MagicMock()
    mock_chunk.id = uuid.uuid4()
    mock_chunk.page_number = 1
    mock_chunk.chunk_index = 0
    mock_chunk.content = "Summary content"
    mock_chunk.token_count = 10
    
    mock_result_chunks = MagicMock()
    mock_result_chunks.scalars().all.return_value = [mock_chunk]
    
    db.execute.side_effect = [mock_result_doc, mock_result_chunks]
    
    res = await tool_summarize_document({"doc_title": "Policy"}, mock_ctx_employee, db)
    assert res.has_relevant_results

async def test_summarize_unauthorized_document(mock_ctx_employee):
    db = AsyncMock(spec=AsyncSession)
    mock_result_doc = MagicMock()
    mock_result_doc.first.return_value = None
    db.execute.side_effect = [mock_result_doc]
    res = await tool_summarize_document({"doc_title": "Secret"}, mock_ctx_employee, db)
    assert not res.has_relevant_results

async def test_compare_authorized_documents(mock_ctx_admin):
    db = AsyncMock(spec=AsyncSession)
    
    doc1 = MagicMock(); doc1.id = uuid.uuid4(); doc1.filename = "Doc1.pdf"
    doc2 = MagicMock(); doc2.id = uuid.uuid4(); doc2.filename = "Doc2.pdf"
    
    res_doc1 = MagicMock(); res_doc1.first.return_value = doc1
    res_doc2 = MagicMock(); res_doc2.first.return_value = doc2
    
    chunk1 = MagicMock(); chunk1.id = uuid.uuid4(); chunk1.page_number=1; chunk1.chunk_index=0; chunk1.content="1"; chunk1.token_count=1
    chunk2 = MagicMock(); chunk2.id = uuid.uuid4(); chunk2.page_number=1; chunk2.chunk_index=0; chunk2.content="2"; chunk2.token_count=1
    
    res_chunk1 = MagicMock(); res_chunk1.scalars().all.return_value = [chunk1]
    res_chunk2 = MagicMock(); res_chunk2.scalars().all.return_value = [chunk2]
    
    db.execute.side_effect = [res_doc1, res_doc2, res_chunk1, res_chunk2]
    
    res = await tool_compare_documents({"doc1_title": "D1", "doc2_title": "D2", "criteria": "X"}, mock_ctx_admin, db)
    assert res.has_relevant_results
    assert len(res.results) == 2

async def test_compare_unauthorized_document(mock_ctx_admin):
    db = AsyncMock(spec=AsyncSession)
    doc1 = MagicMock(); doc1.id = uuid.uuid4(); doc1.filename = "Doc1.pdf"
    res_doc1 = MagicMock(); res_doc1.first.return_value = doc1
    res_doc2 = MagicMock(); res_doc2.first.return_value = None
    db.execute.side_effect = [res_doc1, res_doc2]
    res = await tool_compare_documents({"doc1_title": "D1", "doc2_title": "D2"}, mock_ctx_admin, db)
    assert not res.has_relevant_results

async def test_rag_service_valid_router(mock_ctx_employee, fake_chunk):
    db = AsyncMock(spec=AsyncSession)
    with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = ['{"tool": "standard_rag", "arguments": {"query": "q"}}', "Answer"]
        with patch("app.services.chat.rag_service.TOOL_MAP") as mock_map:
            mock_tool = AsyncMock()
            mock_tool.return_value = RetrievalResponse(query="q", results=[fake_chunk], has_relevant_results=True)
            mock_map.get.return_value = mock_tool
            mock_map.__contains__.return_value = True
            
            res = await rag_service.generate_answer("q", mock_ctx_employee, db)
            assert res.answer == "Answer"
            assert mock_gen.call_count == 2
            mock_tool.assert_called_once()

@pytest.mark.parametrize("router_output", [
    "invalid json", 
    '{"tool": "fake_tool"}', 
    '{"tool": "summarize_document", "arguments": "not_a_dict"}'
])
async def test_rag_service_fallback(mock_ctx_employee, router_output, fake_chunk):
    db = AsyncMock(spec=AsyncSession)
    with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = [router_output, "Answer"]
        with patch("app.services.chat.rag_service.TOOL_MAP") as mock_map:
            mock_tool = AsyncMock()
            mock_tool.return_value = RetrievalResponse(query="q", results=[fake_chunk], has_relevant_results=True)
            # simulate fallback logic which gets standard_rag from map
            mock_map.get.return_value = mock_tool
            # simulate tool is not in map if it's fake_tool
            def mock_contains(key): return key in ["standard_rag", "compare_documents", "summarize_document"]
            mock_map.__contains__.side_effect = mock_contains
            
            res = await rag_service.generate_answer("q", mock_ctx_employee, db)
            assert res.answer == "Answer"
            mock_tool.assert_called_once()
            
async def test_rag_service_core_mechanics(mock_ctx_employee, fake_chunk):
    db = AsyncMock(spec=AsyncSession)
    with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = ['{"tool": "summarize_document", "arguments": {"doc_title": "x"}}', "Summary"]
        with patch("app.services.chat.rag_service.TOOL_MAP") as mock_map:
            mock_tool = AsyncMock()
            mock_tool.return_value = RetrievalResponse(query="x", results=[fake_chunk], has_relevant_results=True)
            mock_map.get.return_value = mock_tool
            mock_map.__contains__.return_value = True
            
            res = await rag_service.generate_answer("q", mock_ctx_employee, db)
            
            mock_tool.assert_called_once()
            assert len(res.retrieved_chunks) == 1
            
            # verify prompt injection
            assert mock_gen.call_count == 2
            kwargs = mock_gen.call_args_list[1].kwargs
            assert "untrusted external data" in kwargs["system_prompt"]
            # assert "untrusted external data" in kwargs["user_prompt"]
            # assert "===DOCUMENT_CONTEXT===" in kwargs["user_prompt"]

async def test_rag_service_router_exception_fallback(mock_ctx_employee, fake_chunk):
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.schemas.retrieval import RetrievalResponse
    from app.services.chat.rag_service import rag_service
    from unittest.mock import AsyncMock, patch
    
    db = AsyncMock(spec=AsyncSession)
    with patch("app.services.chat.rag_service.llm_service.generate_chat", new_callable=AsyncMock) as mock_gen:
        # First call (router) raises Exception
        # Second call (synthesis) succeeds
        mock_gen.side_effect = [Exception("Ollama unreachable"), "Final Answer"]
        with patch("app.services.chat.rag_service.TOOL_MAP") as mock_map:
            mock_tool = AsyncMock()
            mock_tool.return_value = RetrievalResponse(query="q", results=[fake_chunk], has_relevant_results=True)
            mock_map.get.return_value = mock_tool
            def mock_contains(key): return key in ["standard_rag", "compare_documents", "summarize_document"]
            mock_map.__contains__.side_effect = mock_contains
            
            res = await rag_service.generate_answer("q", mock_ctx_employee, db)
            
            assert res.answer == "Final Answer"
            assert mock_gen.call_count == 2
            mock_tool.assert_called_once()
