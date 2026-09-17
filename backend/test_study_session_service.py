from bson import ObjectId

from app.services.study_session_service import create_study_session
from app.database.mongodb import study_sessions_collection


def test_create_study_session():
    user_id = "6aaa6b2c9398c80c9251e142"
    video_id = "pytest-video-123"

    result = create_study_session(
        user_id=user_id,
        video_id=video_id,
        video_url="https://youtube.com/watch?v=pytest-video-123",
        title="Pytest Video",
        original_language="English",
        original_language_code="en",
    )

    assert "id" in result
    assert result["user_id"] == user_id
    assert result["video_id"] == video_id
    assert result["video_url"] == (
        "https://youtube.com/watch?v=pytest-video-123"
    )

    saved_session = study_sessions_collection.find_one({
        "_id": ObjectId(result["id"])
    })

    assert saved_session is not None
    assert saved_session["user_id"] == ObjectId(user_id)
    assert saved_session["video_id"] == video_id

    # Clean up the test document
    study_sessions_collection.delete_one({
        "_id": ObjectId(result["id"])
    })