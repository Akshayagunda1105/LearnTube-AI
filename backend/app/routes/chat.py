
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user_id
from app.schemas.chat import ChatRequest
from app.services.rag_pipeline_service import get_cached_video_rag
from app.services.rag_service import answer_question
from app.services.study_session_service import (
    get_study_session,
    save_chat_message,
)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("")
def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        # Verify that this study session belongs to the user.
        session = get_study_session(
            session_id=request.session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found",
            )

        # Prevent a request from using a different video's RAG data.
        if session["video_id"] != request.video_id:
            raise HTTPException(
                status_code=400,
                detail="Video ID does not match the study session",
            )

        rag_data = get_cached_video_rag(request.video_id)

        if rag_data is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Video has not been processed yet. "
                    "Process the video before asking questions."
                ),
            )

        # Use the existing RAG pipeline to answer the question.
        response = answer_question(
            request.question,
            rag_data["vector_store"],
            top_k=3,
            history=[
                message.model_dump()
                for message in request.history
            ],
        )

        answer = response.get("answer")

        if not isinstance(answer, str):
            raise HTTPException(
                status_code=500,
                detail="The AI returned an invalid response",
            )

        # Save the user's question and the AI response.
        timestamp = datetime.now(timezone.utc)

        save_chat_message(
            session_id=request.session_id,
            user_id=user_id,
            message={
                "role": "user",
                "content": request.question,
                "created_at": timestamp,
            },
        )

        save_chat_message(
            session_id=request.session_id,
            user_id=user_id,
            message={
                "role": "assistant",
                "content": answer,
                "sources": response.get("sources", []),
                "created_at": timestamp,
            },
        )

        return response

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(error)}",
        )
