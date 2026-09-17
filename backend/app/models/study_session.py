from datetime import datetime, timezone


def create_study_session_document(
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
    Create a MongoDB document for a study session.
    """

    if not user_id or not user_id.strip():
        raise ValueError("User ID cannot be empty")

    if not video_id or not video_id.strip():
        raise ValueError("Video ID cannot be empty")

    if not video_url or not video_url.strip():
        raise ValueError("Video URL cannot be empty")

    now = datetime.now(timezone.utc)

    return {
        "user_id": user_id,
        "video_id": video_id,
        "video_url": video_url,
        "title": title,
        "thumbnail": thumbnail,
        "original_language": original_language,
        "original_language_code": original_language_code,
        "original_transcript": original_transcript or [],
        "english_transcript": english_transcript or [],
        "summary": None,
        "notes": [],
        "quiz": [],
        "created_at": now,
        "updated_at": now,
    }