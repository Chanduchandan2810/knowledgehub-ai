from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.api.deps import UserContext
from app.services.retrieval.hybrid_service import hybrid_retrieve_chunks
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def _get_auth_filter(ctx: UserContext):
    if ctx.role == "ADMIN":
        return DocumentPermission.admin_id == ctx.user_id
    return DocumentPermission.employee_id == ctx.user_id

async def tool_standard_rag(
    arguments: dict,
    ctx: UserContext,
    db: AsyncSession
) -> RetrievalResponse:
    query = arguments.get("query", "")
    return await hybrid_retrieve_chunks(query, ctx, db)

async def tool_summarize_document(
    arguments: dict,
    ctx: UserContext,
    db: AsyncSession
) -> RetrievalResponse:
    doc_title = arguments.get("doc_title", "")
    
    # 1. Look up the authorized document
    query = (
        select(Document.id, Document.filename)
        .join(DocumentPermission, DocumentPermission.document_id == Document.id)
        .where(
            and_(
                Document.organization_id == ctx.organization_id,
                _get_auth_filter(ctx),
                Document.filename.ilike(f"%{doc_title}%")
            )
        )
        .limit(1)
    )
    result = await db.execute(query)
    doc = result.first()
    
    if not doc:
        return RetrievalResponse(
            query=f"Summarize {doc_title}",
            results=[],
            has_relevant_results=False
        )
        
    doc_id = doc.id
    doc_filename = doc.filename
    
    # 2. Retrieve top chunks for this document (up to HYBRID_FINAL_TOP_K)
    # We retrieve them ordered by chunk_index to maintain reading order for summarization
    chunk_query = (
        select(DocumentChunk)
        .where(
            and_(
                DocumentChunk.document_id == doc_id,
                DocumentChunk.organization_id == ctx.organization_id
            )
        )
        .order_by(DocumentChunk.chunk_index.asc())
        .limit(settings.HYBRID_FINAL_TOP_K)
    )
    
    chunk_res = await db.execute(chunk_query)
    chunks = chunk_res.scalars().all()
    
    results = [
        RetrievedChunk(
            chunk_id=c.id,
            document_id=doc_id,
            filename=doc_filename,
            page_number=c.page_number,
            chunk_index=c.chunk_index,
            content=c.content,
            distance=0.0,
            similarity=1.0,
            token_count=c.token_count
        ) for c in chunks
    ]
    
    return RetrievalResponse(
        query=f"Summarize {doc_title}",
        results=results,
        has_relevant_results=len(results) > 0
    )

async def tool_compare_documents(
    arguments: dict,
    ctx: UserContext,
    db: AsyncSession
) -> RetrievalResponse:
    doc1_title = arguments.get("doc1_title", "")
    doc2_title = arguments.get("doc2_title", "")
    criteria = arguments.get("criteria", "")
    
    # 1. Lookup both documents (authorization enforced)
    query = (
        select(Document.id, Document.filename)
        .join(DocumentPermission, DocumentPermission.document_id == Document.id)
        .where(
            and_(
                Document.organization_id == ctx.organization_id,
                _get_auth_filter(ctx),
                Document.filename.ilike(f"%{doc1_title}%")
            )
        )
        .limit(1)
    )
    doc1 = (await db.execute(query)).first()
    
    query = (
        select(Document.id, Document.filename)
        .join(DocumentPermission, DocumentPermission.document_id == Document.id)
        .where(
            and_(
                Document.organization_id == ctx.organization_id,
                _get_auth_filter(ctx),
                Document.filename.ilike(f"%{doc2_title}%")
            )
        )
        .limit(1)
    )
    doc2 = (await db.execute(query)).first()
    
    if not doc1 or not doc2:
        return RetrievalResponse(
            query=f"Compare {doc1_title} and {doc2_title}",
            results=[],
            has_relevant_results=False
        )
        
    doc1_id, doc1_filename = doc1.id, doc1.filename
    doc2_id, doc2_filename = doc2.id, doc2.filename
    
    # Retrieve top chunks for doc1
    chunk_query1 = (
        select(DocumentChunk)
        .where(and_(DocumentChunk.document_id == doc1_id, DocumentChunk.organization_id == ctx.organization_id))
        .order_by(DocumentChunk.chunk_index.asc())
        .limit(settings.HYBRID_FINAL_TOP_K // 2)
    )
    chunks1 = (await db.execute(chunk_query1)).scalars().all()
    
    # Retrieve top chunks for doc2
    chunk_query2 = (
        select(DocumentChunk)
        .where(and_(DocumentChunk.document_id == doc2_id, DocumentChunk.organization_id == ctx.organization_id))
        .order_by(DocumentChunk.chunk_index.asc())
        .limit(settings.HYBRID_FINAL_TOP_K // 2)
    )
    chunks2 = (await db.execute(chunk_query2)).scalars().all()
    
    results = []
    for c in chunks1:
        results.append(RetrievedChunk(
            chunk_id=c.id, document_id=doc1_id, filename=doc1_filename,
            page_number=c.page_number, chunk_index=c.chunk_index, content=c.content,
            distance=0.0, similarity=1.0, token_count=c.token_count
        ))
    for c in chunks2:
        results.append(RetrievedChunk(
            chunk_id=c.id, document_id=doc2_id, filename=doc2_filename,
            page_number=c.page_number, chunk_index=c.chunk_index, content=c.content,
            distance=0.0, similarity=1.0, token_count=c.token_count
        ))
        
    return RetrievalResponse(
        query=f"Compare {doc1_filename} and {doc2_filename} based on {criteria}",
        results=results,
        has_relevant_results=len(results) > 0
    )

TOOL_MAP = {
    "standard_rag": tool_standard_rag,
    "compare_documents": tool_compare_documents,
    "summarize_document": tool_summarize_document
}
