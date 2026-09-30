import hashlib
import logging
from typing import Optional
from sqlalchemy import text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.core.config import settings
from app.core.storage import supabase_client

from app.services.documents.extractor import extract_pdf, extract_txt
from app.services.documents.normalizer import normalize_text
from app.services.documents.chunker import DocumentChunker
from app.services.documents.embeddings import get_embedding_service
from app.services.documents.validator import validate_embeddings

logger = logging.getLogger(__name__)

async def atomic_claim_document(session: AsyncSession, document_id: str) -> Optional[Document]:
    """
    Atomically claims a document for processing, preventing concurrent processing.
    Locks documents that are UPLOADED, FAILED, or PROCESSED.
    """
    stmt = text("""
        UPDATE documents
        SET status = :processing_status,
            processing_started_at = NOW(),
            attempt_count = attempt_count + 1,
            error_message = NULL
        WHERE id = CAST(:document_id AS uuid)
          AND status IN (:uploaded, :failed, :processed)
        RETURNING id;
    """).bindparams(
        processing_status=DocumentStatus.PROCESSING.value,
        document_id=document_id,
        uploaded=DocumentStatus.UPLOADED.value,
        failed=DocumentStatus.FAILED.value,
        processed=DocumentStatus.PROCESSED.value
    )
    
    result = await session.execute(stmt)
    row = result.fetchone()
    
    if not row:
        return None
        
    # Document is claimed. Fetch the full ORM object.
    from sqlalchemy import select
    doc_stmt = select(Document).where(Document.id == document_id)
    doc_result = await session.execute(doc_stmt)
    return doc_result.scalar_one_or_none()


async def download_document_from_storage(organization_id: str, storage_path: str) -> bytes:
    """Downloads the raw bytes from Supabase Storage."""
    # The storage_path is stored as "org_id/uuid.ext".
    # Storage API requires the path within the bucket.
    try:
        response = supabase_client.storage.from_("documents").download(storage_path)
        return response
    except Exception as e:
        logger.error(f"Failed to download document from storage: {e}")
        raise ValueError(f"Could not retrieve file from storage: {str(e)}")


async def process_document(document_id: str) -> None:
    """
    Background task to process a document.
    """
    # 1. Atomic Claim
    async with AsyncSessionLocal() as session:
        doc = await atomic_claim_document(session, document_id)
        if not doc:
            logger.info(f"Document {document_id} could not be claimed or is already processing.")
            return
            
        await session.commit()
        
    try:
        # 2. Fetch File
        file_bytes = await download_document_from_storage(str(doc.organization_id), doc.storage_path)
        
        content_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # 3. Extraction
        if doc.mime_type == "application/pdf":
            pages = await extract_pdf(file_bytes)
        elif doc.mime_type == "text/plain":
            pages = await extract_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported mime type for processing: {doc.mime_type}")
            
        # 4. Normalization
        for page in pages:
            page["text"] = normalize_text(page["text"])
            
        # 5. Chunking
        chunker = DocumentChunker(
            model_name=settings.EMBEDDING_MODEL,
            chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
            overlap_percent=settings.CHUNK_OVERLAP_PERCENT
        )
        chunks_data = chunker.chunk_pages(pages, doc.filename)
        
        if not chunks_data:
            raise ValueError("No text content could be extracted from the document.")
            
        if len(chunks_data) > settings.MAX_CHUNK_COUNT:
            raise ValueError(f"Document produced too many chunks ({len(chunks_data)}). Max is {settings.MAX_CHUNK_COUNT}.")
            
        # 6. Embeddings
        embedding_service = get_embedding_service()
        texts_to_embed = [c["content"] for c in chunks_data]
        embeddings = await embedding_service.generate_embeddings(texts_to_embed)
        
        # 7. Validation
        validate_embeddings(embeddings)
        
        # Assemble Final Chunks
        for idx, chunk in enumerate(chunks_data):
            chunk["embedding"] = embeddings[idx]
            
        # 8. Atomic Transaction to Replace Chunks and Update Status
        async with AsyncSessionLocal() as session:
            # Delete old chunks
            await session.execute(
                delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
            )
            
            # Insert new chunks
            for chunk_data in chunks_data:
                new_chunk = DocumentChunk(
                    document_id=doc.id,
                    organization_id=doc.organization_id,
                    chunk_index=chunk_data["chunk_index"],
                    content=chunk_data["content"],
                    embedding=chunk_data["embedding"],
                    page_number=chunk_data["page_number"],
                    token_count=chunk_data["token_count"],
                    metadata_json={}
                )
                session.add(new_chunk)
                
            # Update Document Status
            update_stmt = text("""
                UPDATE documents
                SET status = :processed_status,
                    processed_at = NOW(),
                    content_hash = :hash,
                    chunk_count = :count,
                    embedding_model = :model
                WHERE id = CAST(:id AS uuid)
            """).bindparams(
                processed_status=DocumentStatus.PROCESSED.value,
                hash=content_hash,
                count=len(chunks_data),
                model=settings.EMBEDDING_MODEL,
                id=doc.id
            )
            await session.execute(update_stmt)
            await session.commit()
            
            logger.info(f"Successfully processed document {document_id} into {len(chunks_data)} chunks.")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        # Mark as FAILED
        async with AsyncSessionLocal() as session:
            fail_stmt = text("""
                UPDATE documents
                SET status = :failed_status,
                    error_message = :err
                WHERE id = CAST(:id AS uuid)
            """).bindparams(
                failed_status=DocumentStatus.FAILED.value,
                err=str(e)[:500],
                id=document_id
            )
            await session.execute(fail_stmt)
            await session.commit()
