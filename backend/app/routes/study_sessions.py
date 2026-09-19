from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user_id
from app.schemas.study_session import CreateStudySessionRequest
from app.services.study_session_service import (
    create_study_session,
    get_study_session,
    get_user_study_sessions,
    update_study_session_summary,
)
from app.services.summarizer_service import (
    create_summary_chunks,
    summarize_chunk,
    combine_chunk_summaries,
    generate_final_summary,
)


router = APIRouter(
    prefix="/api/study-sessions",
    tags=["Study Sessions"]
)


@router.post("")
def create_session(
    request: CreateStudySessionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a study session for the authenticated user.
    """

    try:
        return create_study_session(
            user_id=user_id,
            video_id=request.video_id,
            video_url=request.video_url,
            title=request.title,
            thumbnail=request.thumbnail,
            original_language=request.original_language,
            original_language_code=request.original_language_code,
            original_transcript=request.original_transcript,
            english_transcript=request.english_transcript,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("")
def get_sessions(
    user_id: str = Depends(get_current_user_id),
):
    """
    Retrieve all study sessions belonging to the authenticated user.
    """

    try:
        return get_user_study_sessions(user_id)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/{session_id}")
def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Retrieve one study session belonging to the authenticated user.
    """

    try:
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        return session

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/{session_id}/summary")
def generate_session_summary(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Generate and store an AI summary for a study session.
    """

    try:
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        english_transcript = session["english_transcript"]

        if not english_transcript:
            raise HTTPException(
                status_code=400,
                detail="English transcript is not available"
            )

        summary_chunks = create_summary_chunks(
            english_transcript
        )

        chunk_summaries = []

        for chunk in summary_chunks:
            chunk_summary = summarize_chunk(chunk)
            chunk_summaries.append(chunk_summary)

        combined_summaries = combine_chunk_summaries(
            chunk_summaries
        )

        final_summary = generate_final_summary(
            combined_summaries
        )

        updated_session = update_study_session_summary(
            session_id=session_id,
            user_id=user_id,
            summary=final_summary,
        )

        if updated_session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        return {
            "session_id": session_id,
            "summary": final_summary,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(error)}"
        )