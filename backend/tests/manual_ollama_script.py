import asyncio
import os
import sys
import uuid

# Add backend directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.services.chat.rag_service import ContextBuilder, SYSTEM_PROMPT
from app.services.chat.llm_service import llm_service
from app.schemas.retrieval import RetrievedChunk

async def main():
    health = await llm_service.check_health()
    print("Health:", health)
    
    if health["status"] == "healthy":
        print("\nTesting grounded generation...")
        
        # Simulate retrieved chunks
        chunk1 = RetrievedChunk(
            chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), filename="hr_policy.pdf",
            page_number=3, chunk_index=1, content="Employees receive exactly 20 days of annual leave.", 
            distance=0.1, similarity=0.9, token_count=10
        )
        chunk2 = RetrievedChunk(
            chunk_id=uuid.uuid4(), document_id=uuid.uuid4(), filename="benefits.pdf",
            page_number=5, chunk_index=2, content="Health insurance is provided by BlueCross.", 
            distance=0.15, similarity=0.85, token_count=8
        )
        
        context_text = ContextBuilder.build_context([chunk1, chunk2])
        question = "How many days of annual leave do I get, and who provides the health insurance?"
        
        user_prompt = f"""Please answer the following question based on the provided context.

QUESTION:
{question}

CONTEXT:
{context_text}
"""
        try:
            res = await llm_service.generate_chat(SYSTEM_PROMPT, user_prompt)
            print("\nResponse:")
            print(res)
        except Exception as e:
            print("Failed:", e)

if __name__ == "__main__":
    asyncio.run(main())
