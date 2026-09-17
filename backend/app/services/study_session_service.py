from bson import ObjectId

from app.database.mongodb import study_sessions_collection
from app.models.study_session import create_study_session_document


def create_study_session(
    user_id: str,
    video_id: str,
    video_url: str,
    title: str = "",
    thumbnail: str = "",
    original_language: str = "",
    original_language_code: str = "",
    original_transcript: list = None,
    english_transcript: list = None,
):
    """
    Create and store a study session in MongoDB.
    """

    session_document = create_study_session_document(
        user_id=user_id,
        video_id=video_id,
        video_url=video_url,
        title=title,
        thumbnail=thumbnail,
        original_language=original_language,
        original_language_code=original_language_code,
        original_transcript=original_transcript,
        english_transcript=english_transcript,
    )

    result = study_sessions_collection.insert_one(session_document)

    return {
        "id": str(result.inserted_id),
        "user_id": str(session_document["user_id"]),
        "video_id": session_document["video_id"],
        "video_url": session_document["video_url"],
    }