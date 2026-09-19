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


def get_study_session(
    session_id: str,
    user_id: str,
):
    """
    Retrieve a study session belonging to a specific user.
    """

    if not session_id or not session_id.strip():
        raise ValueError("Session ID cannot be empty")

    if not ObjectId.is_valid(session_id):
        raise ValueError("Invalid session ID")

    if not user_id or not user_id.strip():
        raise ValueError("User ID cannot be empty")

    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID")

    session = study_sessions_collection.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id),
    })

    if session is None:
        return None

    return {
        "id": str(session["_id"]),
        "user_id": str(session["user_id"]),
        "video_id": session["video_id"],
        "video_url": session["video_url"],
        "title": session["title"],
        "thumbnail": session["thumbnail"],
        "original_language": session["original_language"],
        "original_language_code": session["original_language_code"],
        "original_transcript": session["original_transcript"],
        "english_transcript": session["english_transcript"],
        "summary": session["summary"],
        "notes": session["notes"],
        "quiz": session["quiz"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
    }


def get_user_study_sessions(
    user_id: str,
):
    """
    Retrieve all study sessions belonging to the authenticated user.
    """

    if not user_id or not user_id.strip():
        raise ValueError("User ID cannot be empty")

    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID")

    sessions = study_sessions_collection.find({
        "user_id": ObjectId(user_id)
    }).sort(
        "created_at",
        -1
    )

    return [
        {
            "id": str(session["_id"]),
            "user_id": str(session["user_id"]),
            "video_id": session["video_id"],
            "video_url": session["video_url"],
            "title": session["title"],
            "thumbnail": session["thumbnail"],
            "original_language": session["original_language"],
            "original_language_code": session["original_language_code"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
        }
        for session in sessions
    ]


def update_study_session_summary(
    session_id: str,
    user_id: str,
    summary: dict,
):
    """
    Update the AI-generated summary of a study session
    belonging to the authenticated user.
    """

    if not session_id or not session_id.strip():
        raise ValueError("Session ID cannot be empty")

    if not ObjectId.is_valid(session_id):
        raise ValueError("Invalid session ID")

    if not user_id or not user_id.strip():
        raise ValueError("User ID cannot be empty")

    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID")

    if not isinstance(summary, dict):
        raise ValueError("Summary must be a dictionary")

    required_fields = [
        "overview",
        "key_points",
        "concepts",
        "takeaways",
    ]

    for field in required_fields:
        if field not in summary:
            raise ValueError(
                f"Summary is missing required field: {field}"
            )

    result = study_sessions_collection.update_one(
        {
            "_id": ObjectId(session_id),
            "user_id": ObjectId(user_id),
        },
        {
            "$set": {
                "summary": summary,
                "updated_at": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ),
            }
        }
    )

    if result.matched_count == 0:
        return None

    return get_study_session(
        session_id=session_id,
        user_id=user_id,
    )