from datetime import datetime, timezone

from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.database.mongodb import study_sessions_collection
from app.services.jwt_service import create_access_token


client = TestClient(app)

USER_ID = "6aaa6b2c9398c80c9251e142"

TEST_VIDEO_ID = "summary_test_video"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=summary_test_video"


def create_test_session():
    now = datetime.now(timezone.utc)

    session = {
        "user_id": ObjectId(USER_ID),
        "video_id": TEST_VIDEO_ID,
        "video_url": TEST_VIDEO_URL,
        "title": "Summary Test Video",
        "thumbnail": "",
        "original_language": "English",
        "original_language_code": "en",
        "original_transcript": [
            {
                "text": "Binary search is a searching algorithm.",
                "start": 0,
                "duration": 5,
            }
        ],
        "english_transcript": [
            {
                "text": "Binary search is a searching algorithm.",
                "start": 0,
                "duration": 5,
            },
            {
                "text": "It works on sorted arrays.",
                "start": 5,
                "duration": 5,
            },
        ],
        "summary": None,
        "notes": [],
        "quiz": [],
        "created_at": now,
        "updated_at": now,
    }

    result = study_sessions_collection.insert_one(session)

    return str(result.inserted_id)


def test_generate_summary_without_token():
    session_id = create_test_session()

    try:
        response = client.post(
            f"/api/study-sessions/{session_id}/summary"
        )

        assert response.status_code == 401

    finally:
        study_sessions_collection.delete_one({
            "_id": ObjectId(session_id)
        })


def test_generate_summary_with_invalid_token():
    session_id = create_test_session()

    try:
        response = client.post(
            f"/api/study-sessions/{session_id}/summary",
            headers={
                "Authorization": "Bearer invalid-token"
            }
        )

        assert response.status_code == 401

    finally:
        study_sessions_collection.delete_one({
            "_id": ObjectId(session_id)
        })


def test_generate_summary_for_nonexistent_session():
    token = create_access_token(USER_ID)

    fake_session_id = str(ObjectId())

    response = client.post(
        f"/api/study-sessions/{fake_session_id}/summary",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_generate_summary_for_valid_session(monkeypatch):
    session_id = create_test_session()

    token = create_access_token(USER_ID)

    fake_summary = {
        "overview": "Binary search efficiently searches sorted arrays.",
        "key_points": [
            "Binary search requires a sorted array.",
            "It repeatedly divides the search space in half.",
        ],
        "concepts": [
            {
                "title": "Binary Search",
                "explanation": (
                    "A searching algorithm that repeatedly "
                    "divides the search space."
                ),
            }
        ],
        "takeaways": [
            "Binary search reduces the search space by half."
        ],
    }

    def mock_summarize_chunk(chunk):
        return {
            "start": chunk[0]["start"],
            "end": (
                chunk[-1]["start"]
                + chunk[-1]["duration"]
            ),
            "summary": "Binary search works on sorted arrays.",
        }

    def mock_generate_final_summary(combined_summaries):
        return fake_summary

    monkeypatch.setattr(
        "app.routes.study_sessions.summarize_chunk",
        mock_summarize_chunk,
    )

    monkeypatch.setattr(
        "app.routes.study_sessions.generate_final_summary",
        mock_generate_final_summary,
    )

    try:
        response = client.post(
            f"/api/study-sessions/{session_id}/summary",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["session_id"] == session_id
        assert data["summary"] == fake_summary

        stored_session = study_sessions_collection.find_one({
            "_id": ObjectId(session_id)
        })

        assert stored_session["summary"] == fake_summary

    finally:
        study_sessions_collection.delete_one({
            "_id": ObjectId(session_id)
        })


def test_generate_summary_for_another_users_session():
    now = datetime.now(timezone.utc)

    other_user_id = "507f1f77bcf86cd799439011"

    session = {
        "user_id": ObjectId(other_user_id),
        "video_id": TEST_VIDEO_ID,
        "video_url": TEST_VIDEO_URL,
        "title": "Other User Video",
        "thumbnail": "",
        "original_language": "English",
        "original_language_code": "en",
        "original_transcript": [],
        "english_transcript": [
            {
                "text": "This belongs to another user.",
                "start": 0,
                "duration": 5,
            }
        ],
        "summary": None,
        "notes": [],
        "quiz": [],
        "created_at": now,
        "updated_at": now,
    }

    result = study_sessions_collection.insert_one(session)
    session_id = str(result.inserted_id)

    token = create_access_token(USER_ID)

    try:
        response = client.post(
            f"/api/study-sessions/{session_id}/summary",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 404

    finally:
        study_sessions_collection.delete_one({
            "_id": ObjectId(session_id)
        })


def test_generate_summary_without_english_transcript():
    now = datetime.now(timezone.utc)

    session = {
        "user_id": ObjectId(USER_ID),
        "video_id": "no_transcript_video",
        "video_url": (
            "https://www.youtube.com/watch?v=no_transcript_video"
        ),
        "title": "No Transcript Video",
        "thumbnail": "",
        "original_language": "English",
        "original_language_code": "en",
        "original_transcript": [],
        "english_transcript": [],
        "summary": None,
        "notes": [],
        "quiz": [],
        "created_at": now,
        "updated_at": now,
    }

    result = study_sessions_collection.insert_one(session)
    session_id = str(result.inserted_id)

    token = create_access_token(USER_ID)

    try:
        response = client.post(
            f"/api/study-sessions/{session_id}/summary",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 400

        assert response.json()["detail"] == (
            "English transcript is not available"
        )

    finally:
        study_sessions_collection.delete_one({
            "_id": ObjectId(session_id)
        })