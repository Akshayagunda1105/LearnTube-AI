from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.database.mongodb import study_sessions_collection
from app.services.jwt_service import create_access_token


client = TestClient(app)

USER_ID = "6aaa6b2c9398c80c9251e142"


def test_create_session_without_token():
    response = client.post(
        "/api/study-sessions",
        json={
            "video_id": "route-test-no-token",
            "video_url": "https://youtube.com/watch?v=route-test-no-token",
            "title": "No Token Test",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_session_with_invalid_token():
    response = client.post(
        "/api/study-sessions",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        json={
            "video_id": "route-test-invalid-token",
            "video_url": "https://youtube.com/watch?v=route-test-invalid-token",
            "title": "Invalid Token Test",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_create_session_with_valid_token():
    token = create_access_token(USER_ID)

    response = client.post(
        "/api/study-sessions",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "video_id": "route-test-valid-token",
            "video_url": "https://youtube.com/watch?v=route-test-valid-token",
            "title": "Valid Token Test",
            "original_language": "English",
            "original_language_code": "en",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["user_id"] == USER_ID
    assert data["video_id"] == "route-test-valid-token"

    saved_session = study_sessions_collection.find_one({
        "_id": ObjectId(data["id"])
    })

    assert saved_session is not None
    assert saved_session["user_id"] == ObjectId(USER_ID)

    study_sessions_collection.delete_one({
        "_id": ObjectId(data["id"])
    })


def test_create_session_validation_error():
    token = create_access_token(USER_ID)

    response = client.post(
        "/api/study-sessions",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "video_id": "",
            "video_url": "https://youtube.com/watch?v=test",
            "title": "Validation Test",
        },
    )

    assert response.status_code == 422