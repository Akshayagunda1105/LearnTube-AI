from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.database.mongodb import study_sessions_collection
from app.services.jwt_service import create_access_token
from app.services.study_session_service import create_study_session

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

def test_get_sessions_without_token():
    response = client.get("/api/study-sessions")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_sessions_with_valid_token():
    token = create_access_token(USER_ID)

    test_session = create_study_session(
        user_id=USER_ID,
        video_id="history-route-test",
        video_url="https://youtube.com/watch?v=history-route-test",
        title="History Route Test",
    )

    response = client.get(
        "/api/study-sessions",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    matching_sessions = [
        session
        for session in data
        if session["id"] == test_session["id"]
    ]

    assert len(matching_sessions) == 1
    assert matching_sessions[0]["user_id"] == USER_ID
    assert matching_sessions[0]["video_id"] == "history-route-test"

    study_sessions_collection.delete_one({
        "_id": ObjectId(test_session["id"])
    })


def test_get_specific_session_with_valid_token():
    token = create_access_token(USER_ID)

    test_session = create_study_session(
        user_id=USER_ID,
        video_id="specific-route-test",
        video_url="https://youtube.com/watch?v=specific-route-test",
        title="Specific Session Test",
    )

    response = client.get(
        f"/api/study-sessions/{test_session['id']}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_session["id"]
    assert data["user_id"] == USER_ID
    assert data["video_id"] == "specific-route-test"
    assert data["title"] == "Specific Session Test"

    study_sessions_collection.delete_one({
        "_id": ObjectId(test_session["id"])
    })


def test_get_specific_session_without_token():
    response = client.get(
        "/api/study-sessions/507f1f77bcf86cd799439011"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_session_belonging_to_another_user():
    token = create_access_token(USER_ID)

    another_user_id = "507f1f77bcf86cd799439012"

    test_session = create_study_session(
        user_id=another_user_id,
        video_id="another-user-session",
        video_url="https://youtube.com/watch?v=another-user-session",
        title="Another User Session",
    )

    response = client.get(
        f"/api/study-sessions/{test_session['id']}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Study session not found"

    study_sessions_collection.delete_one({
        "_id": ObjectId(test_session["id"])
    })


def test_get_nonexistent_session():
    token = create_access_token(USER_ID)

    nonexistent_session_id = "507f1f77bcf86cd799439013"

    response = client.get(
        f"/api/study-sessions/{nonexistent_session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Study session not found"


def test_get_session_with_invalid_id():
    token = create_access_token(USER_ID)

    response = client.get(
        "/api/study-sessions/invalid-session-id",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid session ID"