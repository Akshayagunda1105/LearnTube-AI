
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.middleware.auth import get_current_user_id


client = TestClient(app)


def fake_current_user_id():
    return "test-user-123"


def test_chat_returns_fallback_answer_and_saves_messages():
    fallback_answer = (
        "I cannot answer this question because the "
        "information is not available in the video context."
    )

    sources = [
        {
            "chunk_id": "chunk_0001",
            "text": "The video explains the basics of machine learning.",
            "start": 10.0,
            "end": 25.0,
            "distance": 0.5,
        }
    ]

    session = {
        "session_id": "test-session-123",
        "user_id": "test-user-123",
        "video_id": "test-video-123",
    }

    app.dependency_overrides[get_current_user_id] = (
        fake_current_user_id
    )

    try:
        with (
            patch(
                "app.routes.chat.get_study_session",
                return_value=session,
            ),
            patch(
                "app.routes.chat.get_cached_video_rag",
                return_value={"vector_store": object()},
            ),
            patch(
                "app.routes.chat.answer_question",
                return_value={
                    "answer": fallback_answer,
                    "sources": sources,
                },
            ) as mock_answer,
            patch(
                "app.routes.chat.save_chat_message"
            ) as mock_save,
        ):
            response = client.post(
                "/api/chat",
                json={
                    "session_id": "test-session-123",
                    "video_id": "test-video-123",
                    "question": "What is the capital of Japan?",
                    "history": [],
                },
            )

        assert response.status_code == 200
        assert response.json()["answer"] == fallback_answer
        assert response.json()["sources"] == sources

        mock_answer.assert_called_once_with(
            "What is the capital of Japan?",
            mock_answer.call_args.args[1],
            top_k=3,
            history=[],
        )

        assert mock_save.call_count == 2

        saved_messages = [
            call.kwargs["message"]
            for call in mock_save.call_args_list
        ]

        assert saved_messages[0]["role"] == "user"
        assert (
            saved_messages[0]["content"]
            == "What is the capital of Japan?"
        )

        assert saved_messages[1]["role"] == "assistant"
        assert saved_messages[1]["content"] == fallback_answer
        assert saved_messages[1]["sources"] == sources

    finally:
        app.dependency_overrides.pop(
            get_current_user_id, None
        )
