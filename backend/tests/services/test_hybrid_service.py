"""Phase 7 — Hybrid Search Tests

Covers:
- Vector retrieval (preserved Phase 5 behavior)
- Keyword retrieval
- Score normalization
- Hybrid fusion (deduplication, agreement bonus, ordering)
- Permission/security isolation
- Edge cases (empty results, single source, both empty)
- Retrieval evaluation (semantic vs keyword vs hybrid)
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.retrieval.hybrid_service import (
    hybrid_retrieve_chunks,
    _vector_retrieve,
    _keyword_retrieve,
    _normalize_scores,
    _fuse_results,
    _permission_filter,
)
from app.api.deps import UserContext
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.schemas.retrieval import RetrievedChunk
from app.core.config import settings

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_ctx():
    return UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="ADMIN",
        email="admin@test.com",
        full_name="Test Admin",
    )

@pytest.fixture
def employee_ctx():
    return UserContext(
        user_id=uuid.uuid4(),
        auth_user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="EMPLOYEE",
        email="emp@test.com",
        full_name="Test Employee",
    )

def _make_chunk(content="Test content", chunk_index=0, page_number=1):
    return DocumentChunk(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        chunk_index=chunk_index,
        content=content,
        page_number=page_number,
        token_count=10,
    )

def _make_doc(doc_id=None, filename="test.pdf"):
    d = Document(id=doc_id or uuid.uuid4(), filename=filename)
    d.organization_id = uuid.uuid4()
    return d


# ---------------------------------------------------------------------------
# 7.2 — Score normalization tests
# ---------------------------------------------------------------------------

class TestNormalization:
    def test_empty_list(self):
        assert _normalize_scores([]) == []

    def test_single_value(self):
        assert _normalize_scores([0.5]) == [1.0]

    def test_identical_values(self):
        assert _normalize_scores([0.3, 0.3, 0.3]) == [1.0, 1.0, 1.0]

    def test_two_values(self):
        result = _normalize_scores([0.0, 1.0])
        assert result == [0.0, 1.0]

    def test_three_values(self):
        result = _normalize_scores([0.2, 0.5, 0.8])
        assert abs(result[0] - 0.0) < 1e-9
        assert abs(result[1] - 0.5) < 1e-9
        assert abs(result[2] - 1.0) < 1e-9

    def test_negative_values(self):
        result = _normalize_scores([-1.0, 0.0, 1.0])
        assert abs(result[0] - 0.0) < 1e-9
        assert abs(result[1] - 0.5) < 1e-9
        assert abs(result[2] - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# 7.6 — Fusion tests
# ---------------------------------------------------------------------------

class TestFusion:
    def test_vector_only_results(self):
        """When keyword search returns nothing, vector results still appear."""
        chunk = _make_chunk("Employees get 20 leave days")
        doc = _make_doc(filename="policy.pdf")
        chunk.id = uuid.uuid4()

        vector_results = [(chunk, doc, 0.3)]  # distance 0.3, within threshold
        keyword_results = []

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 1
        assert fused[0].retrieval_method == "vector"
        assert fused[0].keyword_score is None
        assert fused[0].vector_score is not None

    def test_keyword_only_results(self):
        """When vector search returns nothing, keyword results still appear."""
        chunk = _make_chunk("Policy HR-2026-WFH-17 details")
        doc = _make_doc(filename="hr_policy.pdf")
        chunk.id = uuid.uuid4()

        vector_results = []
        keyword_results = [(chunk, doc, 0.05)]  # ts_rank score

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 1
        assert fused[0].retrieval_method == "keyword"
        assert fused[0].vector_score is None
        assert fused[0].keyword_score is not None

    def test_both_empty(self):
        """When both searches return nothing, fusion returns empty."""
        fused = _fuse_results([], [], threshold=0.65)
        assert len(fused) == 0

    def test_deduplication(self):
        """Same chunk from both sources appears only once with hybrid method."""
        chunk = _make_chunk("Leave policy content")
        doc = _make_doc(filename="handbook.pdf")

        vector_results = [(chunk, doc, 0.2)]
        keyword_results = [(chunk, doc, 0.08)]

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 1
        assert fused[0].retrieval_method == "hybrid"
        # Both scores should be set
        assert fused[0].vector_score is not None
        assert fused[0].keyword_score is not None

    def test_agreement_bonus(self):
        """Hybrid chunks score higher than vector-only or keyword-only."""
        shared_chunk = _make_chunk("Shared content")
        shared_doc = _make_doc(filename="shared.pdf")

        vector_only_chunk = _make_chunk("Vector only content")
        vector_only_doc = _make_doc(filename="vector.pdf")

        # Make distances identical so the only difference is the agreement bonus
        vector_results = [
            (shared_chunk, shared_doc, 0.2),
            (vector_only_chunk, vector_only_doc, 0.2),
        ]
        keyword_results = [(shared_chunk, shared_doc, 0.05)]

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 2

        # The hybrid chunk should rank first due to agreement bonus
        assert fused[0].chunk_id == shared_chunk.id
        assert fused[0].retrieval_method == "hybrid"
        assert fused[1].retrieval_method == "vector"

    def test_threshold_filtering(self):
        """Chunks with distance above threshold are filtered out."""
        chunk_near = _make_chunk("Near chunk")
        doc_near = _make_doc(filename="near.pdf")

        chunk_far = _make_chunk("Far chunk")
        doc_far = _make_doc(filename="far.pdf")

        vector_results = [
            (chunk_near, doc_near, 0.3),   # within threshold
            (chunk_far, doc_far, 0.9),     # above threshold
        ]

        fused = _fuse_results(vector_results, [], threshold=0.65)
        assert len(fused) == 1
        assert fused[0].chunk_id == chunk_near.id

    def test_deterministic_ordering(self):
        """Results with same score are ordered by chunk_id for determinism."""
        chunk_a = _make_chunk("A")
        chunk_b = _make_chunk("B")
        doc = _make_doc(filename="doc.pdf")

        # Same distance = same score
        vector_results = [
            (chunk_a, doc, 0.3),
            (chunk_b, doc, 0.3),
        ]

        fused = _fuse_results(vector_results, [], threshold=0.65)
        assert len(fused) == 2
        # Should be sorted by chunk_id string for ties
        expected_order = sorted([chunk_a.id, chunk_b.id], key=str)
        assert fused[0].chunk_id == expected_order[0]
        assert fused[1].chunk_id == expected_order[1]

    def test_citation_metadata_preserved(self):
        """Fused results preserve all metadata needed for citations."""
        chunk = _make_chunk("Content with citations", page_number=5, chunk_index=3)
        doc = _make_doc(filename="important_doc.pdf")

        fused = _fuse_results([(chunk, doc, 0.2)], [], threshold=0.65)
        assert len(fused) == 1
        result = fused[0]
        assert result.filename == "important_doc.pdf"
        assert result.page_number == 5
        assert result.chunk_index == 3
        assert result.content == "Content with citations"
        assert result.token_count == 10
        assert result.document_id == doc.id
        assert result.chunk_id == chunk.id


# ---------------------------------------------------------------------------
# 7.7 — Permission / security tests
# ---------------------------------------------------------------------------

class TestPermissionSecurity:
    def test_admin_permission_filter(self, admin_ctx):
        """Admin uses admin_id filter."""
        from app.models.document_permission import DocumentPermission
        pf = _permission_filter(admin_ctx)
        # The filter should reference admin_id
        assert "admin_id" in str(pf)

    def test_employee_permission_filter(self, employee_ctx):
        """Employee uses employee_id filter."""
        from app.models.document_permission import DocumentPermission
        pf = _permission_filter(employee_ctx)
        # The filter should reference employee_id
        assert "employee_id" in str(pf)

    async def test_vector_query_includes_org_filter(self, admin_ctx):
        """Vector retrieval query includes organization_id filter."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        await _vector_retrieve([0.0] * 384, admin_ctx, mock_db, limit=5)

        query_obj = mock_db.execute.call_args[0][0]
        compiled = str(query_obj.compile(compile_kwargs={"literal_binds": True}))
        assert "document_chunks.organization_id =" in compiled
        assert "documents.organization_id =" in compiled
        assert admin_ctx.organization_id.hex in compiled

    async def test_keyword_query_includes_org_filter(self, admin_ctx):
        """Keyword retrieval query includes organization_id filter."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        await _keyword_retrieve("test query", admin_ctx, mock_db, limit=5)

        # Verify the query was executed
        mock_db.execute.assert_called_once()
        query_obj = mock_db.execute.call_args[0][0]
        # Compile without literal_binds to avoid REGCONFIG render issue
        compiled = str(query_obj.compile())
        assert "document_chunks.organization_id =" in compiled
        assert "documents.organization_id =" in compiled
        assert "document_permissions" in compiled

    async def test_cross_org_isolation(self):
        """Two different orgs produce queries with different org parameters."""
        org_a = uuid.uuid4()
        org_b = uuid.uuid4()

        ctx_a = UserContext(
            user_id=uuid.uuid4(), auth_user_id=uuid.uuid4(),
            organization_id=org_a, role="ADMIN",
            email="a@test.com", full_name="A"
        )
        ctx_b = UserContext(
            user_id=uuid.uuid4(), auth_user_id=uuid.uuid4(),
            organization_id=org_b, role="ADMIN",
            email="b@test.com", full_name="B"
        )

        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        # Use vector retrieve which doesn't have REGCONFIG issue
        await _vector_retrieve([0.0] * 384, ctx_a, mock_db, limit=5)
        compiled_a = str(mock_db.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))

        await _vector_retrieve([0.0] * 384, ctx_b, mock_db, limit=5)
        compiled_b = str(mock_db.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))

        assert org_a.hex in compiled_a
        assert org_b.hex in compiled_b
        assert org_a.hex not in compiled_b
        assert org_b.hex not in compiled_a

    async def test_employee_keyword_uses_employee_permission(self, employee_ctx):
        """Employee keyword search uses employee_id permission filter."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        await _keyword_retrieve("policy", employee_ctx, mock_db, limit=5)

        query_obj = mock_db.execute.call_args[0][0]
        # Compile without literal_binds to avoid REGCONFIG render issue
        compiled = str(query_obj.compile())
        assert "document_permissions.employee_id =" in compiled


# ---------------------------------------------------------------------------
# 7.10 — Hybrid retrieval integration tests
# ---------------------------------------------------------------------------

class TestHybridRetrieve:
    async def test_empty_query(self, admin_ctx):
        """Empty query returns empty results without DB call."""
        mock_db = AsyncMock()
        result = await hybrid_retrieve_chunks("   ", admin_ctx, mock_db)
        assert result.has_relevant_results is False
        assert len(result.results) == 0
        mock_db.execute.assert_not_called()

    async def test_full_pipeline(self, admin_ctx):
        """Full pipeline: embedding → vector + keyword → fusion → results."""
        chunk1 = _make_chunk("Annual leave is 20 days")
        doc1 = _make_doc(filename="leave.pdf")

        chunk2 = _make_chunk("Sick leave policy details")
        doc2 = _make_doc(filename="sick.pdf")

        mock_result_vector = MagicMock()
        mock_result_vector.all.return_value = [(chunk1, doc1, 0.2)]

        mock_result_keyword = MagicMock()
        mock_result_keyword.all.return_value = [(chunk2, doc2, 0.04)]

        mock_db = AsyncMock()
        # First call = vector, second call = keyword
        mock_db.execute.side_effect = [mock_result_vector, mock_result_keyword]

        with patch(
            "app.services.retrieval.hybrid_service.get_embedding_service"
        ) as mock_embed:
            mock_embed.return_value.generate_embeddings = AsyncMock(
                return_value=[[0.0] * 384]
            )
            result = await hybrid_retrieve_chunks("leave days", admin_ctx, mock_db)

        assert result.has_relevant_results is True
        assert len(result.results) == 2
        # Both chunks should be present
        chunk_ids = {r.chunk_id for r in result.results}
        assert chunk1.id in chunk_ids
        assert chunk2.id in chunk_ids

    async def test_no_results(self, admin_ctx):
        """When both searches return empty, has_relevant_results is False."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        with patch(
            "app.services.retrieval.hybrid_service.get_embedding_service"
        ) as mock_embed:
            mock_embed.return_value.generate_embeddings = AsyncMock(
                return_value=[[0.0] * 384]
            )
            result = await hybrid_retrieve_chunks("nonsense xyz", admin_ctx, mock_db)

        assert result.has_relevant_results is False
        assert len(result.results) == 0

    async def test_top_k_limit(self, admin_ctx):
        """Results are limited to HYBRID_FINAL_TOP_K."""
        chunks_and_docs = []
        for i in range(15):
            c = _make_chunk(f"Chunk {i}")
            d = _make_doc(filename=f"doc{i}.pdf")
            chunks_and_docs.append((c, d, 0.1 + i * 0.02))

        mock_result_vector = MagicMock()
        mock_result_vector.all.return_value = chunks_and_docs[:10]

        mock_result_keyword = MagicMock()
        mock_result_keyword.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [mock_result_vector, mock_result_keyword]

        with patch(
            "app.services.retrieval.hybrid_service.get_embedding_service"
        ) as mock_embed:
            mock_embed.return_value.generate_embeddings = AsyncMock(
                return_value=[[0.0] * 384]
            )
            result = await hybrid_retrieve_chunks("test", admin_ctx, mock_db)

        assert len(result.results) <= settings.HYBRID_FINAL_TOP_K


# ---------------------------------------------------------------------------
# 7.18 — Retrieval quality evaluation
# ---------------------------------------------------------------------------

class TestRetrievalQualityEvaluation:
    """Deterministic retrieval evaluation demonstrating when each
    search method provides value."""

    def test_semantic_wins(self):
        """Semantic search finds meaning even without exact keyword match.

        Query: 'vacation days' matches chunk about 'annual leave'
        (no shared keywords, but semantically equivalent).
        Vector finds it; keyword does not.
        """
        chunk = _make_chunk("Employees are entitled to 18 days of annual leave.")
        doc = _make_doc(filename="handbook.pdf")

        vector_results = [(chunk, doc, 0.15)]  # strong semantic match
        keyword_results = []  # no keyword match for 'vacation'

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 1
        assert fused[0].retrieval_method == "vector"
        assert "annual leave" in fused[0].content

    def test_keyword_wins(self):
        """Keyword search finds exact identifiers that embeddings miss.

        Query: 'HR-2026-WFH-17' — exact policy identifier.
        Keyword search can match this directly via full-text search.
        Vector search may not find a strong semantic match for an ID.
        """
        chunk = _make_chunk("Policy HR-2026-WFH-17 governs remote work eligibility.")
        doc = _make_doc(filename="policies.pdf")

        vector_results = []  # embedding doesn't match well on IDs
        keyword_results = [(chunk, doc, 0.12)]  # exact term match

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 1
        assert fused[0].retrieval_method == "keyword"
        assert "HR-2026-WFH-17" in fused[0].content

    def test_hybrid_wins(self):
        """Hybrid search promotes chunks found by both methods.

        Query: 'sick leave policy' matches semantically AND by keyword.
        The agreement bonus pushes this chunk above vector-only results.
        """
        shared_chunk = _make_chunk("The sick leave policy allows up to 12 days per year.")
        shared_doc = _make_doc(filename="leave_policy.pdf")

        other_chunk = _make_chunk("General attendance policy overview.")
        other_doc = _make_doc(filename="attendance.pdf")

        vector_results = [
            (shared_chunk, shared_doc, 0.15),   # semantic match
            (other_chunk, other_doc, 0.15),      # same distance
        ]
        keyword_results = [
            (shared_chunk, shared_doc, 0.08),    # keyword match too
        ]

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 2
        # The shared chunk should rank FIRST due to agreement bonus
        assert fused[0].chunk_id == shared_chunk.id
        assert fused[0].retrieval_method == "hybrid"
        assert fused[0].hybrid_score > fused[1].hybrid_score

    def test_permission_matters(self):
        """Even with high scores, unauthorized results must be filterable.

        This test validates that the fusion layer preserves document_id
        so that downstream citation validation can reject unauthorized docs.
        """
        authorized_chunk = _make_chunk("Authorized content about payroll.")
        authorized_doc = _make_doc(filename="payroll.pdf")

        # In real execution, unauthorized chunks would never reach fusion
        # because the SQL query includes permission JOINs.
        # This test verifies metadata preservation.
        fused = _fuse_results(
            [(authorized_chunk, authorized_doc, 0.2)], [], threshold=0.65
        )
        assert len(fused) == 1
        assert fused[0].document_id == authorized_doc.id
        assert fused[0].filename == "payroll.pdf"

    def test_no_relevant_results(self):
        """When nothing passes threshold, no results are returned."""
        chunk = _make_chunk("Unrelated content")
        doc = _make_doc(filename="random.pdf")

        # Distance above threshold
        vector_results = [(chunk, doc, 0.9)]
        keyword_results = []

        fused = _fuse_results(vector_results, keyword_results, threshold=0.65)
        assert len(fused) == 0
