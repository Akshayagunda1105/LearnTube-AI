from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.services.jwt_service import (
    create_access_token,
    decode_access_token,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)


def test_create_and_decode_access_token():
    user_id = "test-user-id"

    token = create_access_token(user_id)
    payload = decode_access_token(token)

    assert payload["sub"] == user_id
    assert "iat" in payload
    assert "exp" in payload


def test_empty_user_id():
    with pytest.raises(ValueError, match="User ID cannot be empty"):
        create_access_token("")


def test_empty_token():
    with pytest.raises(ValueError, match="Token cannot be empty"):
        decode_access_token("")


def test_invalid_token():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("invalid-token")


def test_expired_token():
    now = datetime.now(timezone.utc)

    payload = {
        "sub": "test-user-id",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
    }

    expired_token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    with pytest.raises(ValueError, match="Token has expired"):
        decode_access_token(expired_token)