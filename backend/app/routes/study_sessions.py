from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user_id
from app.schemas.study_session import CreateStudySessionRequest
from app.services.study_session_service import create_study_session


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

from app.services.study_session_service import (
    create_study_session,
    get_study_session,
    get_user_study_sessions,
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