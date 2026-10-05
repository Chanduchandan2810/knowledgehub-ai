import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging
from datetime import datetime, timezone

from app.db.session import get_db
from app.api.deps import get_current_user_context, UserContext
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.citation import Citation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ChatResponse
)
from app.services.chat.rag_service import rag_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conv_in: ConversationCreate,
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    new_conv = Conversation(
        organization_id=ctx.organization_id,
        auth_user_id=ctx.auth_user_id,
        title=conv_in.title if conv_in.title and conv_in.title.strip() else "New Conversation"
    )
    db.add(new_conv)
    await db.commit()
    await db.refresh(new_conv)
    return new_conv

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """List conversations belonging to the current user."""
    query = (
        select(Conversation)
        .where(
            Conversation.organization_id == ctx.organization_id,
            Conversation.auth_user_id == ctx.auth_user_id
        )
        .order_by(desc(Conversation.updated_at))
    )
    result = await db.execute(query)
    conversations = result.scalars().all()
    return conversations

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.organization_id == ctx.organization_id,
        Conversation.auth_user_id == ctx.auth_user_id
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conv

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    conversation_id: uuid.UUID,
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """List messages for a specific conversation."""
    # Verify ownership
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.organization_id == ctx.organization_id,
        Conversation.auth_user_id == ctx.auth_user_id
    )
    result = await db.execute(conv_query)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    result = await db.execute(msg_query)
    msgs = result.scalars().all()

    doc_ids = set()
    for m in msgs:
        for c in m.citations:
            doc_ids.add(c.document_id)

    if doc_ids:
        from app.models.document import Document
        doc_query = select(Document.id, Document.filename).where(Document.id.in_(doc_ids))
        doc_result = await db.execute(doc_query)
        doc_map = {doc_id: filename for doc_id, filename in doc_result.fetchall()}

        for m in msgs:
            for c in m.citations:
                c.filename = doc_map.get(c.document_id)

    return msgs

@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: uuid.UUID,
    msg_in: MessageCreate,
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """Send a message, trigger RAG generation, and return the response."""
    # 1. Validate input
    content = msg_in.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message content cannot be empty.")
    if len(content) > 4000:
        raise HTTPException(status_code=422, detail="Message content too long.")

    # 2. Verify conversation ownership
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.organization_id == ctx.organization_id,
        Conversation.auth_user_id == ctx.auth_user_id
    )
    result = await db.execute(conv_query)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Update conversation title if it's still the default and this is the first message
    # A simple deterministic strategy
    if conv.title == "New Conversation":
        new_title = content[:40].strip()
        if len(content) > 40:
            new_title += "..."
        conv.title = new_title

    # 3. Persist USER message
    user_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=content
    )
    db.add(user_msg)

    # Update conversation's updated_at
    conv.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user_msg)

    # 4. Trigger RAG Generation
    try:
        rag_res = await rag_service.generate_answer(content, ctx, db)
    except Exception as e:
        logger.error(f"RAG generation failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI generation service is currently unavailable. Your message was saved."
        )

    # 5. Persist ASSISTANT message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=rag_res.answer
    )
    db.add(assistant_msg)

    # We must flush to get assistant_msg.id for citations
    await db.flush()

    # 6. Persist Citations (ignoring duplicates via logic, already validated in RAGService)
    citation_objects = []
    for cited_chunk in rag_res.citations:
        citation = Citation(
            message_id=assistant_msg.id,
            chunk_id=cited_chunk.chunk_id,
            document_id=cited_chunk.document_id
        )
        db.add(citation)
        citation_objects.append(citation)

    # Touch conversation again so updated_at reflects assistant response
    conv.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(assistant_msg)

    # Attach for immediate Pydantic serialization
    assistant_msg.citations = citation_objects

    return ChatResponse(
        user_message=user_msg,
        assistant_message=assistant_msg
    )

from fastapi.responses import StreamingResponse
import json as json_lib

@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: uuid.UUID,
    msg_in: MessageCreate,
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """Stream a message and trigger RAG generation."""
    content = msg_in.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message content cannot be empty.")
    if len(content) > 4000:
        raise HTTPException(status_code=422, detail="Message content too long.")

    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.organization_id == ctx.organization_id,
        Conversation.auth_user_id == ctx.auth_user_id
    )
    result = await db.execute(conv_query)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conv.title == "New Conversation":
        new_title = content[:40].strip()
        if len(content) > 40:
            new_title += "..."
        conv.title = new_title

    user_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=content
    )
    db.add(user_msg)
    conv.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user_msg)

    async def event_generator():
        yield f"event: start\ndata: {json_lib.dumps({'message_id': str(user_msg.id)})}\n\n"

        answer_acc = ""
        validated_citations = []

        try:
            async for chunk in rag_service.generate_answer_stream(content, ctx, db):
                if chunk["type"] == "token":
                    answer_acc += chunk["text"]
                    yield f"event: token\ndata: {json_lib.dumps({'text': chunk['text']})}\n\n"
                elif chunk["type"] == "citations":
                    validated_citations = chunk["citations"]
                    cit_data = []
                    for c in validated_citations:
                        cit_data.append({
                            "chunk_id": str(c.chunk_id),
                            "document_id": str(c.document_id),
                            "filename": getattr(c, "filename", None)
                        })
                    yield f"event: citations\ndata: {json_lib.dumps({'citations': cit_data})}\n\n"

            # 5. Persist ASSISTANT message
            assistant_msg = Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=answer_acc
            )
            db.add(assistant_msg)
            await db.flush()

            # 6. Persist Citations
            for cited_chunk in validated_citations:
                citation = Citation(
                    message_id=assistant_msg.id,
                    chunk_id=cited_chunk.chunk_id,
                    document_id=cited_chunk.document_id
                )
                db.add(citation)

            conv.updated_at = datetime.now(timezone.utc)
            await db.commit()

            yield f"event: done\ndata: {json_lib.dumps({'message_id': str(assistant_msg.id)})}\n\n"

        except Exception as e:
            logger.error(f"RAG streaming generation failed: {e}")
            yield f"event: error\ndata: {json_lib.dumps({'message': 'AI generation service is currently unavailable. Your message was saved.'})}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)
