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
    return result.scalars().all()

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
