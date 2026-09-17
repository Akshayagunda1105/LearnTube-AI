import pytest
from bson import ObjectId

from app.database.mongodb import study_sessions_collection
from app.services.study_session_service import (
    create_study_session,
    get_study_session,
    get_user_study_sessions,
)


USER_ID = "6aaa6b2c9398c80c9251e142"
OTHER_USER_ID = "507f1f77bcf86cd799439011"


def test_create_study_session():
    video_id = "pytest-video-123"

    result = create_study_session(
        user_id=USER_ID,
        video_id=video_id,
        video_url="https://youtube.com/watch?v=pytest-video-123",
        title="Pytest Video",
        original_language="English",
        original_language_code="en",
    )

    assert "id" in result
    assert result["user_id"] == USER_ID
    assert result["video_id"] == video_id

    saved_session = study_sessions_collection.find_one({
        "_id": ObjectId(result["id"])
    })

    assert saved_session is not None
    assert saved_session["user_id"] == ObjectId(USER_ID)
    assert saved_session["video_id"] == video_id

    study_sessions_collection.delete_one({
        "_id": ObjectId(result["id"])
    })


def test_get_study_session():
    video_id = "pytest-get-video"

    result = create_study_session(
        user_id=USER_ID,
        video_id=video_id,
        video_url="https://youtube.com/watch?v=pytest-get-video",
        title="Get Test Video",
    )

    session = get_study_session(
        session_id=result["id"],
        user_id=USER_ID,
    )

    assert session is not None
    assert session["id"] == result["id"]
    assert session["user_id"] == USER_ID
    assert session["video_id"] == video_id
    assert session["title"] == "Get Test Video"

    study_sessions_collection.delete_one({
        "_id": ObjectId(result["id"])
    })


def test_user_cannot_access_another_users_session():
    video_id = "pytest-owner-video"

    result = create_study_session(
        user_id=USER_ID,
        video_id=video_id,
        video_url="https://youtube.com/watch?v=pytest-owner-video",
    )

    session = get_study_session(
        session_id=result["id"],
        user_id=OTHER_USER_ID,
    )

    assert session is None

    study_sessions_collection.delete_one({
        "_id": ObjectId(result["id"])
    })


def test_get_nonexistent_session():
    fake_session_id = "507f1f77bcf86cd799439012"

    session = get_study_session(
        session_id=fake_session_id,
        user_id=USER_ID,
    )

    assert session is None


def test_empty_session_id():
    with pytest.raises(ValueError, match="Session ID cannot be empty"):
        get_study_session(
            session_id="",
            user_id=USER_ID,
        )


def test_invalid_session_id():
    with pytest.raises(ValueError, match="Invalid session ID"):
        get_study_session(
            session_id="invalid-id",
            user_id=USER_ID,
        )


def test_empty_user_id():
    with pytest.raises(ValueError, match="User ID cannot be empty"):
        get_study_session(
            session_id="507f1f77bcf86cd799439012",
            user_id="",
        )


def test_invalid_user_id():
    with pytest.raises(ValueError, match="Invalid user ID"):
        get_study_session(
            session_id="507f1f77bcf86cd799439012",
            user_id="invalid-user-id",
        )


def test_get_user_study_sessions():
    video_id_1 = "pytest-history-video-1"
    video_id_2 = "pytest-history-video-2"

    session_1 = create_study_session(
        user_id=USER_ID,
        video_id=video_id_1,
        video_url="https://youtube.com/watch?v=pytest-history-video-1",
        title="History Video 1",
    )

    session_2 = create_study_session(
        user_id=USER_ID,
        video_id=video_id_2,
        video_url="https://youtube.com/watch?v=pytest-history-video-2",
        title="History Video 2",
    )

    sessions = get_user_study_sessions(USER_ID)

    session_ids = [session["id"] for session in sessions]

    assert session_1["id"] in session_ids
    assert session_2["id"] in session_ids

    for session in sessions:
        assert session["user_id"] == USER_ID

    study_sessions_collection.delete_many({
        "_id": {
            "$in": [
                ObjectId(session_1["id"]),
                ObjectId(session_2["id"]),
            ]
        }
    })


def test_user_history_does_not_include_another_users_sessions():
    own_session = create_study_session(
        user_id=USER_ID,
        video_id="pytest-own-history",
        video_url="https://youtube.com/watch?v=pytest-own-history",
        title="Own Session",
    )

    other_session = create_study_session(
        user_id=OTHER_USER_ID,
        video_id="pytest-other-history",
        video_url="https://youtube.com/watch?v=pytest-other-history",
        title="Other User Session",
    )

    sessions = get_user_study_sessions(USER_ID)

    session_ids = [session["id"] for session in sessions]

    assert own_session["id"] in session_ids
    assert other_session["id"] not in session_ids

    study_sessions_collection.delete_many({
        "_id": {
            "$in": [
                ObjectId(own_session["id"]),
                ObjectId(other_session["id"]),
            ]
        }
    })


def test_empty_user_history():
    temporary_user_id = "507f1f77bcf86cd799439013"

    sessions = get_user_study_sessions(temporary_user_id)

    assert sessions == []


def test_empty_user_id_for_history():
    with pytest.raises(ValueError, match="User ID cannot be empty"):
        get_user_study_sessions("")


def test_invalid_user_id_for_history():
    with pytest.raises(ValueError, match="Invalid user ID"):
        get_user_study_sessions("invalid-user-id")