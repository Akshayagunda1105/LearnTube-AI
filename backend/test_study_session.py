import pytest
from bson import ObjectId

from app.models.study_session import create_study_session_document


def test_create_study_session_document():
    user_id = "6aaa6b2c9398c80c9251e142"

    session = create_study_session_document(
        user_id=user_id,
        video_id="abc123",
        video_url="https://youtube.com/watch?v=abc123",
        title="Python Tutorial",
        original_language="Telugu",
        original_language_code="te",
    )

    assert session["user_id"] == ObjectId(user_id)
    assert isinstance(session["user_id"], ObjectId)

    assert session["video_id"] == "abc123"
    assert session["video_url"] == "https://youtube.com/watch?v=abc123"
    assert session["title"] == "Python Tutorial"
    assert session["original_language"] == "Telugu"
    assert session["original_language_code"] == "te"


def test_default_values():
    session = create_study_session_document(
        user_id="6aaa6b2c9398c80c9251e142",
        video_id="abc123",
        video_url="https://youtube.com/watch?v=abc123",
    )

    assert session["original_transcript"] == []
    assert session["english_transcript"] == []
    assert session["summary"] is None
    assert session["notes"] == []
    assert session["quiz"] == []


def test_empty_user_id():
    with pytest.raises(ValueError, match="User ID cannot be empty"):
        create_study_session_document(
            user_id="",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
        )


def test_invalid_user_id():
    with pytest.raises(ValueError, match="Invalid user ID"):
        create_study_session_document(
            user_id="invalid-id",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
        )


def test_empty_video_id():
    with pytest.raises(ValueError, match="Video ID cannot be empty"):
        create_study_session_document(
            user_id="6aaa6b2c9398c80c9251e142",
            video_id="",
            video_url="https://youtube.com/watch?v=abc123",
        )


def test_empty_video_url():
    with pytest.raises(ValueError, match="Video URL cannot be empty"):
        create_study_session_document(
            user_id="6aaa6b2c9398c80c9251e142",
            video_id="abc123",
            video_url="",
        )