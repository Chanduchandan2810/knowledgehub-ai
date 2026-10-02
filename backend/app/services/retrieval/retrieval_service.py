import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.api.deps import UserContext
from app.services.documents.embeddings import get_embedding_service
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.core.config import settings

async def retrieve_chunks(
    question: str,
    ctx: UserContext,
    db: AsyncSession
) -> RetrievalResponse:
    # 1. Clean query
    clean_question = question.strip()
    if not clean_question:
        return RetrievalResponse(
            query=clean_question,
            results=[],
            has_relevant_results=False
        )

    # 2. Get embeddings
    embed_svc = get_embedding_service()
    embeddings = await embed_svc.generate_embeddings([clean_question])
    question_embedding = embeddings[0]

    # 3. Construct explicitly authorized query
    # The user must have a matching organization_id and a row in document_permissions
    permission_filter = (DocumentPermission.admin_id == ctx.user_id) if ctx.role == "ADMIN" else (DocumentPermission.employee_id == ctx.user_id)

    # Calculate distance using pgvector cosine distance operator <=>
    distance_col = DocumentChunk.embedding.cosine_distance(question_embedding).label("distance")

    query = (
        select(DocumentChunk, Document, distance_col)
        .join(Document, Document.id == DocumentChunk.document_id)
        .join(DocumentPermission, DocumentPermission.document_id == Document.id)
        .where(
            and_(
                DocumentChunk.organization_id == ctx.organization_id,
                Document.organization_id == ctx.organization_id,
                permission_filter
            )
        )
        .order_by(distance_col)
        .limit(settings.RETRIEVAL_TOP_K)
    )

    result = await db.execute(query)
    rows = result.all()

    # 4. Filter by threshold and build response
    results = []
    has_relevant_results = False

    for chunk, doc, distance in rows:
        # Cosine distance: smaller is better (0 is exact match, 2 is exact opposite)
        # We convert to a similarity score (1 - distance) for UI convenience
        similarity = 1.0 - distance
        
        # Check threshold
        if distance <= settings.RETRIEVAL_THRESHOLD_COSINE_DISTANCE:
            has_relevant_results = True
            
        results.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=doc.id,
                filename=doc.filename,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                distance=distance,
                similarity=similarity,
                token_count=chunk.token_count
            )
        )
        
    # If no chunk passed the threshold, we return the results but flag it as not genuinely relevant
    return RetrievalResponse(
        query=clean_question,
        results=results,
        has_relevant_results=has_relevant_results
    )
