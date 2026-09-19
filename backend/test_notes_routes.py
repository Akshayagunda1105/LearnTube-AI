from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.database.mongodb import study_sessions_collection
from app.services.study_session_service import create_study_session
from app.middleware.auth import get_current_user_id


client = TestClient(app)


USER_ID = "6aaa6b2c9398c80c9251e142"
OTHER_USER_ID = "507f1f77bcf86cd799439011"


def set_test_user(user_id):
    """
    Override JWT authentication with a controlled test user.
    """

    app.dependency_overrides[
        get_current_user_id
    ] = lambda: user_id


def clear_test_user():
    """
    Clear authentication dependency overrides.
    """

    app.dependency_overrides.clear()


def create_test_session():
    """
    Create a study session containing an English transcript.
    """

    result = create_study_session(
        user_id=USER_ID,
        video_id="notes-api-test-video",
        video_url="https://youtube.com/watch?v=notes-api-test-video",
        title="Notes API Test Video",
        original_language="English",
        original_language_code="en",
        original_transcript=[
            {
                "text": "Machine learning allows systems to learn from data.",
                "start": 0,
                "duration": 5,
            }
        ],
        english_transcript=[
            {
                "text": "Machine learning allows systems to learn from data.",
                "start": 0,
                "duration": 5,
            }
        ],
    )

    return result["id"]


def test_notes_endpoint_requires_authentication():
    clear_test_user()

    response = client.post(
        "/api/study-sessions/507f1f77bcf86cd799439011/notes"
    )

    assert response.status_code == 401


def test_notes_endpoint_rejects_invalid_token():
    clear_test_user()

    response = client.post(
        "/api/study-sessions/507f1f77bcf86cd799439011/notes",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401


def test_notes_endpoint_returns_404_for_nonexistent_session():
    set_test_user(USER_ID)

    try:
        response = client.post(
            "/api/study-sessions/507f1f77bcf86cd799439011/notes"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Study session not found"
        )

    finally:
        clear_test_user()


def test_notes_endpoint_rejects_another_users_session():
    set_test_user(OTHER_USER_ID)

    try:
        session_id = create_test_session()

        response = client.post(
            f"/api/study-sessions/{session_id}/notes"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Study session not found"
        )

    finally:
        clear_test_user()


def test_notes_endpoint_rejects_missing_transcript():
    set_test_user(USER_ID)

    try:
        result = create_study_session(
            user_id=USER_ID,
            video_id="notes-no-transcript-video",
            video_url=(
                "https://youtube.com/watch?v="
                "notes-no-transcript-video"
            ),
            title="No Transcript Video",
            original_language="English",
            original_language_code="en",
            original_transcript=[],
            english_transcript=[],
        )

        session_id = result["id"]

        response = client.post(
            f"/api/study-sessions/{session_id}/notes"
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "English transcript is not available"
        )

    finally:
        clear_test_user()


def test_notes_endpoint_generates_and_persists_notes(
    monkeypatch
):
    set_test_user(USER_ID)

    try:
        session_id = create_test_session()

        fake_note_section = {
            "title": "Introduction to Machine Learning",
            "timestamp": 0,
            "points": [
                "Machine learning allows systems to learn from data."
            ],
        }

        def mock_generate_chunk_notes(chunk):
            return fake_note_section

        monkeypatch.setattr(
            "app.routes.study_sessions.generate_chunk_notes",
            mock_generate_chunk_notes,
        )

        response = client.post(
            f"/api/study-sessions/{session_id}/notes"
        )

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["session_id"] == session_id

        assert response_data["notes"] == {
            "sections": [
                fake_note_section
            ]
        }

        stored_session = study_sessions_collection.find_one({
            "_id": ObjectId(session_id)
        })

        assert stored_session is not None

        assert stored_session["notes"] == {
            "sections": [
                fake_note_section
            ]
        }

    finally:
        clear_test_user()