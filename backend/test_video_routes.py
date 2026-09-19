from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.database.mongodb import study_sessions_collection
from app.services.jwt_service import create_access_token

client = TestClient(app)

USER_ID = "6aaa6b2c9398c80c9251e142"


def test_process_video_without_token():
    response = client.post(
        "/api/videos/process",
        json={
            "video_id": "route-video-no-token",
            "video_url": "https://youtube.com/watch?v=route-video-no-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_process_video_with_valid_token(monkeypatch):
    token = create_access_token(USER_ID)

    fake_rag_data = {
        "video_id": "route-video-valid",
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "original_segments": [
            {
                "text": "Machine learning is useful.",
                "start": 0.0,
                "duration": 3.0,
            }
        ],
        "english_segments": [
            {
                "text": "Machine learning is useful.",
                "start": 0.0,
                "duration": 3.0,
            }
        ],
        "rag_chunks": [
            {
                "text": "Machine learning is useful.",
                "start": 0.0,
                "end": 3.0,
            }
        ],
    }

    def fake_get_video_rag(video_id):
        assert video_id == "route-video-valid"
        return fake_rag_data

    def fake_create_study_session(
        user_id,
        video_id,
        video_url,
        title="",
        thumbnail="",
        original_language="",
        original_language_code="",
        original_transcript=None,
        english_transcript=None,
    ):
        assert user_id == USER_ID
        assert video_id == "route-video-valid"
        assert video_url == (
            "https://youtube.com/watch?v=route-video-valid"
        )

        assert original_language == "English"
        assert original_language_code == "en"
        assert original_transcript == fake_rag_data["original_segments"]
        assert english_transcript == fake_rag_data["english_segments"]

        return {
            "id": "507f1f77bcf86cd799439011",
            "user_id": USER_ID,
            "video_id": video_id,
            "video_url": video_url,
        }

    monkeypatch.setattr(
        "app.routes.videos.get_video_rag",
        fake_get_video_rag,
    )

    monkeypatch.setattr(
        "app.routes.videos.create_study_session",
        fake_create_study_session,
    )

    response = client.post(
        "/api/videos/process",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "video_id": "route-video-valid",
            "video_url": "https://youtube.com/watch?v=route-video-valid",
        },
    )

    print("RESPONSE STATUS:", response.status_code)
    print("RESPONSE BODY:", response.text)

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "507f1f77bcf86cd799439011"
    assert data["video_id"] == "route-video-valid"
    assert data["language"] == "English"
    assert data["language_code"] == "en"
    assert data["is_generated"] is False
    assert data["chunk_count"] == 1
    assert data["message"] == "Video processed successfully"


def test_process_video_does_not_accept_missing_video_url():
    token = create_access_token(USER_ID)

    response = client.post(
        "/api/videos/process",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "video_id": "missing-url-test",
        },
    )

    assert response.status_code == 422

def test_process_video_creates_study_session_in_database(monkeypatch):
    token = create_access_token(USER_ID)

    fake_rag_data = {
        "video_id": "database-video-test",
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "original_segments": [
            {
                "text": "This is a database test.",
                "start": 0.0,
                "duration": 3.0,
            }
        ],
        "english_segments": [
            {
                "text": "This is a database test.",
                "start": 0.0,
                "duration": 3.0,
            }
        ],
        "rag_chunks": [
            {
                "text": "This is a database test.",
                "start": 0.0,
                "end": 3.0,
            }
        ],
    }

    monkeypatch.setattr(
        "app.routes.videos.get_video_rag",
        lambda video_id: fake_rag_data,
    )

    response = client.post(
        "/api/videos/process",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "video_id": "database-video-test",
            "video_url": "https://youtube.com/watch?v=database-video-test",
        },
    )

    assert response.status_code == 200

    data = response.json()

    session = study_sessions_collection.find_one({
        "_id": ObjectId(data["session_id"])
    })

    assert session is not None
    assert session["user_id"] == ObjectId(USER_ID)
    assert session["video_id"] == "database-video-test"
    assert session["video_url"] == (
        "https://youtube.com/watch?v=database-video-test"
    )
    assert session["original_language"] == "English"
    assert session["original_language_code"] == "en"
    assert session["original_transcript"] == (
        fake_rag_data["original_segments"]
    )
    assert session["english_transcript"] == (
        fake_rag_data["english_segments"]
    )

    study_sessions_collection.delete_one({
        "_id": ObjectId(data["session_id"])
    })