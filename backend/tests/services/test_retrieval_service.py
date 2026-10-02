import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.retrieval.retrieval_service import retrieve_chunks
from app.api.deps import UserContext
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.core.config import settings

@pytest.mark.asyncio
async def test_retrieve_chunks_threshold_filtering():
    # Setup mock user
    mock_ctx = UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="EMPLOYEE",
        email="test@test.com",
        full_name="Test User"
    )

    # Setup mock DB session
    mock_db = AsyncMock()
    mock_result = MagicMock()
    
    # Create fake chunks and docs
    chunk1 = DocumentChunk(id=uuid.uuid4(), page_number=1, chunk_index=1, content="Relevant chunk", token_count=10)
    doc1 = Document(id=uuid.uuid4(), filename="relevant.pdf")
    
    chunk2 = DocumentChunk(id=uuid.uuid4(), page_number=2, chunk_index=2, content="Irrelevant chunk", token_count=10)
    doc2 = Document(id=uuid.uuid4(), filename="irrelevant.pdf")
    
    # Setup returned rows from DB: (chunk, doc, distance)
    # One passes the threshold (0.5 <= 0.65), one fails (0.8 > 0.65)
    mock_result.all.return_value = [
        (chunk1, doc1, 0.5),   # Passes threshold
        (chunk2, doc2, 0.8),   # Fails threshold
    ]
    mock_db.execute.return_value = mock_result

    # Mock embeddings
    mock_embed_svc = AsyncMock()
    mock_embed_svc.generate_embeddings.return_value = [[0.1] * 384]

    with patch('app.services.retrieval.retrieval_service.get_embedding_service', return_value=mock_embed_svc):
        # 1. Test query with mixed results
        res = await retrieve_chunks("test query", mock_ctx, mock_db)
        
        # Should only contain chunk1
        assert res.has_relevant_results is True
        assert len(res.results) == 1
        assert res.results[0].chunk_id == chunk1.id
        assert res.results[0].distance == 0.5
        assert res.results[0].similarity == 0.5

        # 2. Test "yes" query that fails threshold entirely (e.g., all returned chunks are weak)
        mock_result.all.return_value = [
            (chunk2, doc2, 0.9),   # Fails threshold
            (chunk2, doc2, 0.95),  # Fails threshold
        ]
        
        res_weak = await retrieve_chunks("yes", mock_ctx, mock_db)
        
        # Should be completely empty
        assert res_weak.has_relevant_results is False
        assert len(res_weak.results) == 0
