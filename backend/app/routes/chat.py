from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest
from app.services.rag_pipeline_service import get_cached_video_rag
from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.post("")
def chat(request: ChatRequest):
    try:
        # Get the already processed RAG data
        rag_data = get_cached_video_rag(request.video_id)

        # The video must be processed before asking questions
        if rag_data is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Video has not been processed yet. "
                    "Process the video before asking questions."
                )
            )

        # Ask the question using the cached vector store
        response = answer_question(
            request.question,
            rag_data["vector_store"],
            top_k=3
        )

        return response

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(error)}"
        )