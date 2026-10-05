"""Phase 7 — Hybrid Search Service

Combines PostgreSQL vector similarity search (Phase 5) with PostgreSQL
full-text keyword search to improve retrieval quality.

Architecture:
  1. Vector retrieval: pgvector cosine distance via HNSW index
  2. Keyword retrieval: PostgreSQL tsvector + GIN index
  3. Score normalization: min-max into [0, 1]
  4. Fusion: weighted combination with agreement bonus for chunks
     found by both methods
  5. Deduplication: by chunk_id
  6. Deterministic ranking: by hybrid_score desc, then chunk_id for ties

Security:
  Both retrieval paths apply identical authorization filters:
  - organization_id isolation
  - document_permissions JOIN (admin_id or employee_id)

Scoring strategy:
  hybrid_score = (HYBRID_VECTOR_WEIGHT * norm_vector_score)
               + (HYBRID_KEYWORD_WEIGHT * norm_keyword_score)
               + (HYBRID_AGREEMENT_BONUS if found by both methods)

  Default weights: vector=0.7, keyword=0.3, agreement_bonus=0.1

Reranking:
  Deterministic reranking is achieved through the agreement bonus.
  Chunks retrieved by BOTH semantic and lexical search receive a score
  boost, naturally promoting results where meaning AND terminology align.
  This is a lightweight, zero-cost reranking strategy that requires no
  external model.
"""
import uuid
import logging
from typing import Dict, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.api.deps import UserContext
from app.services.documents.embeddings import get_embedding_service
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Authorization helpers (shared by both retrieval paths)
# ---------------------------------------------------------------------------

def _permission_filter(ctx: UserContext):
    """Returns the SQLAlchemy permission filter based on user role."""
    if ctx.role == "ADMIN":
        return DocumentPermission.admin_id == ctx.user_id
    return DocumentPermission.employee_id == ctx.user_id


def _base_auth_query(base_select, ctx: UserContext):
    """
    Applies the standard authorization JOIN chain:
    document_chunks → documents → document_permissions
    with organization_id isolation on both chunks and documents.
    """
    return (
        base_select
        .join(Document, Document.id == DocumentChunk.document_id)
        .join(DocumentPermission, DocumentPermission.document_id == Document.id)
        .where(
            and_(
                DocumentChunk.organization_id == ctx.organization_id,
                Document.organization_id == ctx.organization_id,
                _permission_filter(ctx)
            )
        )
    )


# ---------------------------------------------------------------------------
# Vector retrieval (reuses Phase 5 logic)
# ---------------------------------------------------------------------------

async def _vector_retrieve(
    question_embedding: List[float],
    ctx: UserContext,
    db: AsyncSession,
    limit: int
) -> List[Tuple]:
    """Performs permission-aware vector similarity search."""
    distance_col = DocumentChunk.embedding.cosine_distance(
        question_embedding
    ).label("distance")

    query = _base_auth_query(
        select(DocumentChunk, Document, distance_col),
        ctx
    ).order_by(distance_col).limit(limit)

    result = await db.execute(query)
    return result.all()


# ---------------------------------------------------------------------------
# Keyword retrieval (Phase 7 — PostgreSQL full-text search)
# ---------------------------------------------------------------------------

async def _keyword_retrieve(
    question: str,
    ctx: UserContext,
    db: AsyncSession,
    limit: int
) -> List[Tuple]:
    """Performs permission-aware PostgreSQL full-text keyword search.

    Uses websearch_to_tsquery for flexible query parsing:
    - supports OR, quoted phrases, negation
    - gracefully handles natural-language input
    - falls back gracefully for single terms

    The ts_rank function scores relevance based on term frequency.
    """
    # websearch_to_tsquery handles natural language well:
    #   "sick leave policy"  → 'sick' & 'leave' & 'policy'
    #   "HR-2026-WFH-17"    → 'hr-2026-wfh-17' (exact term)
    tsquery = func.websearch_to_tsquery('english', question)

    rank_col = func.ts_rank(
        DocumentChunk.content_tsv,
        tsquery
    ).label("rank")

    query = _base_auth_query(
        select(DocumentChunk, Document, rank_col),
        ctx
    ).where(
        DocumentChunk.content_tsv.op('@@')(tsquery)
    ).order_by(rank_col.desc()).limit(limit)

    result = await db.execute(query)
    return result.all()


# ---------------------------------------------------------------------------
# Score normalization
# ---------------------------------------------------------------------------

def _normalize_scores(scores: List[float]) -> List[float]:
    """Min-max normalizes a list of scores to [0, 1].

    If all scores are identical, returns 1.0 for each (all equally relevant).
    """
    if not scores:
        return []
    min_s = min(scores)
    max_s = max(scores)
    if max_s == min_s:
        return [1.0] * len(scores)
    return [(s - min_s) / (max_s - min_s) for s in scores]


# ---------------------------------------------------------------------------
# Hybrid fusion
# ---------------------------------------------------------------------------

def _fuse_results(
    vector_results: List[Tuple],
    keyword_results: List[Tuple],
    threshold: float
) -> List[RetrievedChunk]:
    """Fuses vector and keyword results with score normalization,
    deduplication, agreement bonus, and deterministic ranking.

    Steps:
    1. Normalize vector distances → similarity scores in [0, 1]
    2. Normalize keyword ts_rank scores into [0, 1]
    3. Build a unified map keyed by chunk_id
    4. Compute hybrid_score with configurable weights + agreement bonus
    5. Apply relevance threshold (using vector distance where available)
    6. Sort deterministically by hybrid_score desc, then chunk_id
    """
    vector_weight = settings.HYBRID_VECTOR_WEIGHT
    keyword_weight = settings.HYBRID_KEYWORD_WEIGHT
    agreement_bonus = settings.HYBRID_AGREEMENT_BONUS

    # --- Collect raw scores ---
    vector_distances = [dist for _, _, dist in vector_results]
    keyword_ranks = [rank for _, _, rank in keyword_results]

    # --- Normalize ---
    # Vector: convert distance (lower=better) to similarity (higher=better)
    vector_similarities = [1.0 - d for d in vector_distances]
    norm_vector = _normalize_scores(vector_similarities)
    norm_keyword = _normalize_scores(keyword_ranks)

    # --- Build unified candidate map ---
    # Key: chunk_id (UUID), Value: dict with chunk data and scores
    candidates: Dict[uuid.UUID, dict] = {}

    for i, (chunk, doc, distance) in enumerate(vector_results):
        cid = chunk.id
        candidates[cid] = {
            "chunk": chunk,
            "doc": doc,
            "distance": distance,
            "similarity": 1.0 - distance,
            "norm_vector": norm_vector[i],
            "norm_keyword": 0.0,
            "method": "vector",
        }

    for i, (chunk, doc, rank) in enumerate(keyword_results):
        cid = chunk.id
        if cid in candidates:
            # Found by both — mark as hybrid and add keyword score
            candidates[cid]["norm_keyword"] = norm_keyword[i]
            candidates[cid]["method"] = "hybrid"
        else:
            # Keyword-only result: no vector distance available.
            # Use a synthetic distance within threshold so the chunk
            # is eligible, but ranked below vector-confirmed results.
            synthetic_distance = threshold * 0.9
            candidates[cid] = {
                "chunk": chunk,
                "doc": doc,
                "distance": synthetic_distance,
                "similarity": 1.0 - synthetic_distance,
                "norm_vector": 0.0,
                "norm_keyword": norm_keyword[i],
                "method": "keyword",
            }

    # --- Compute hybrid scores and apply threshold ---
    fused: List[RetrievedChunk] = []

    for cid, c in candidates.items():
        # Apply vector distance threshold (skip chunks too far from query).
        # For keyword-only results, synthetic distance is within threshold.
        if c["distance"] > threshold:
            continue

        is_hybrid = c["method"] == "hybrid"
        hybrid_score = (
            vector_weight * c["norm_vector"]
            + keyword_weight * c["norm_keyword"]
            + (agreement_bonus if is_hybrid else 0.0)
        )

        fused.append(
            RetrievedChunk(
                chunk_id=c["chunk"].id,
                document_id=c["doc"].id,
                filename=c["doc"].filename,
                page_number=c["chunk"].page_number,
                chunk_index=c["chunk"].chunk_index,
                content=c["chunk"].content,
                distance=c["distance"],
                similarity=c["similarity"],
                token_count=c["chunk"].token_count,
                vector_score=c["norm_vector"] if c["norm_vector"] > 0 else None,
                keyword_score=c["norm_keyword"] if c["norm_keyword"] > 0 else None,
                hybrid_score=hybrid_score,
                retrieval_method=c["method"],
            )
        )

    # --- Deterministic sort: hybrid_score desc, then chunk_id for ties ---
    fused.sort(key=lambda r: (-r.hybrid_score, str(r.chunk_id)))

    return fused


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def hybrid_retrieve_chunks(
    question: str,
    ctx: UserContext,
    db: AsyncSession
) -> RetrievalResponse:
    """Main hybrid retrieval entry point.

    Performs both vector and keyword search, fuses the results,
    and returns the top-k authorized chunks.

    This function is a drop-in replacement for the Phase 5
    `retrieve_chunks` function — it returns the same RetrievalResponse
    schema and preserves all citation-required metadata.
    """
    # 1. Clean query
    clean_question = question.strip()
    if not clean_question:
        return RetrievalResponse(
            query=clean_question,
            results=[],
            has_relevant_results=False
        )

    # 2. Generate embedding for vector search
    embed_svc = get_embedding_service()
    embeddings = await embed_svc.generate_embeddings([clean_question])
    question_embedding = embeddings[0]

    # 3. Execute both retrieval paths
    # Both paths apply identical authorization filters
    vector_results = await _vector_retrieve(
        question_embedding, ctx, db,
        limit=settings.HYBRID_VECTOR_CANDIDATES
    )
    keyword_results = await _keyword_retrieve(
        clean_question, ctx, db,
        limit=settings.HYBRID_KEYWORD_CANDIDATES
    )

    logger.info(
        f"Hybrid retrieval: {len(vector_results)} vector candidates, "
        f"{len(keyword_results)} keyword candidates"
    )

    # 4. Fuse, normalize, deduplicate, and rank
    fused = _fuse_results(
        vector_results,
        keyword_results,
        threshold=settings.RETRIEVAL_THRESHOLD_COSINE_DISTANCE
    )

    # 5. Apply final top-k limit
    final_results = fused[:settings.HYBRID_FINAL_TOP_K]

    has_relevant = len(final_results) > 0

    return RetrievalResponse(
        query=clean_question,
        results=final_results,
        has_relevant_results=has_relevant
    )
