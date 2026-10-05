from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user_context, UserContext
from app.schemas.retrieval import RetrievalRequest, RetrievalResponse
from app.services.retrieval.hybrid_service import hybrid_retrieve_chunks

router = APIRouter()

@router.post("", response_model=RetrievalResponse, status_code=status.HTTP_200_OK)
async def perform_retrieval(
    request: RetrievalRequest,
    ctx: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Takes a user question, embeds it using the local embedding model, and performs 
    an authorized hybrid search (vector + keyword) to find the most relevant 
    document chunks. Both Admins and Employees can use this endpoint.
    Access is explicitly validated against document_permissions.
    """
    try:
        response = await hybrid_retrieve_chunks(request.question, ctx, db)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform retrieval: {str(e)}"
        )
