import pytest
import uuid
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.citation import Citation

def test_conversation_model():
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    conv = Conversation(
        organization_id=org_id,
        auth_user_id=user_id,
        title="Test Conversation"
    )
    
    assert conv.organization_id == org_id
    assert conv.auth_user_id == user_id
    assert conv.title == "Test Conversation"

def test_conversation_ownership_authorization():
    # Simulate the query pattern that will be used in the service layer
    # to enforce user ownership of conversations.
    from sqlalchemy import select
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    query = select(Conversation).where(
        (Conversation.organization_id == org_id) & 
        (Conversation.auth_user_id == user_id)
    )
    
    # Verify the compiled query contains the required constraints
    compiled = str(query.compile(compile_kwargs={"literal_binds": True}))
    assert "conversations.organization_id =" in compiled
    assert "conversations.auth_user_id =" in compiled

def test_message_model():
    conv_id = uuid.uuid4()
    
    msg = Message(
        conversation_id=conv_id,
        role=MessageRole.USER.value,
        content="Hello world"
    )
    
    assert msg.conversation_id == conv_id
    assert msg.role == "USER"
    assert msg.content == "Hello world"

def test_citation_model():
    msg_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    
    cit = Citation(
        message_id=msg_id,
        chunk_id=chunk_id,
        document_id=doc_id
    )
    
    assert cit.message_id == msg_id
    assert cit.chunk_id == chunk_id
    assert cit.document_id == doc_id
