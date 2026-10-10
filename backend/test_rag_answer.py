
from unittest.mock import MagicMock, patch

import pytest

from app.services.rag_service import (
    UNSUPPORTED_ANSWER,
    answer_question,
    build_context,
    generate_rag_answer,
    validate_answer_support,
    validate_answer_with_context,
)


RESULTS = [
    {
        "chunk_id": "chunk_0001",
        "text": (
            "Supervised learning uses labeled examples "
            "to train a model to make predictions on new data."
        ),
        "start": 8.0,
        "end": 16.0,
        "distance": 0.4,
    },
    {
        "chunk_id": "chunk_0002",
        "text": (
            "Unsupervised learning works with unlabeled data "
            "and can discover hidden patterns or structures."
        ),
        "start": 16.0,
        "end": 24.0,
        "distance": 0.7,
    },
]


# --------------------------------------------------
# Context building tests
# --------------------------------------------------

def test_build_context():
    context = build_context(RESULTS)

    assert isinstance(context, str)
    assert "Supervised learning" in context
    assert "Unsupervised learning" in context


def test_build_context_rejects_empty_results():
    with pytest.raises(
        ValueError,
        match="No retrieved results available",
    ):
        build_context([])


# --------------------------------------------------
# Answer generation tests
# --------------------------------------------------

@patch("app.services.rag_service.client")
def test_generate_rag_answer(mock_client):
    expected_answer = (
        "Supervised learning trains a model using labeled examples "
        "so it can make predictions on new data."
    )

    mock_response = MagicMock()
    mock_response.text = expected_answer
    mock_client.models.generate_content.return_value = mock_response

    answer = generate_rag_answer(
        "How does supervised learning work?",
        build_context(RESULTS),
    )

    assert answer == expected_answer
    mock_client.models.generate_content.assert_called_once()


@patch("app.services.rag_service.client")
def test_generate_rag_answer_preserves_unsupported_question_fallback(
    mock_client,
):
    mock_response = MagicMock()
    mock_response.text = UNSUPPORTED_ANSWER
    mock_client.models.generate_content.return_value = mock_response

    answer = generate_rag_answer(
        "What is the capital of Japan?",
        build_context(RESULTS),
    )

    assert answer == UNSUPPORTED_ANSWER
    mock_client.models.generate_content.assert_called_once()


@patch("app.services.rag_service.client")
def test_generate_rag_answer_rejects_empty_response(mock_client):
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client.models.generate_content.return_value = mock_response

    with pytest.raises(
        ValueError,
        match="Gemini returned an empty answer",
    ):
        generate_rag_answer(
            "Explain supervised learning",
            build_context(RESULTS),
        )


@patch("app.services.rag_service.client")
def test_generate_rag_answer_propagates_api_error(mock_client):
    mock_client.models.generate_content.side_effect = RuntimeError(
        "Simulated Gemini failure"
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated Gemini failure",
    ):
        generate_rag_answer(
            "Explain supervised learning",
            build_context(RESULTS),
        )


# --------------------------------------------------
# Answer validation decision tests
# --------------------------------------------------

def test_validate_answer_support_returns_supported_answer():
    answer = "Supervised learning uses labeled examples."

    result = validate_answer_support(
        answer,
        is_supported=True,
    )

    assert result == answer


def test_validate_answer_support_returns_fallback_when_unsupported():
    result = validate_answer_support(
        "The capital of Japan is Tokyo.",
        is_supported=False,
    )

    assert result == UNSUPPORTED_ANSWER


def test_validate_answer_support_returns_fallback_when_uncertain():
    result = validate_answer_support(
        "Some proposed answer.",
        is_supported=None,
    )

    assert result == UNSUPPORTED_ANSWER


def test_validate_answer_support_rejects_empty_answer():
    with pytest.raises(
        ValueError,
        match="Answer cannot be empty",
    ):
        validate_answer_support(
            "",
            is_supported=True,
        )


# --------------------------------------------------
# Gemini evidence checker tests
# --------------------------------------------------

@patch("app.services.rag_service.client")
def test_validate_answer_with_context_accepts_supported_answer(
    mock_client,
):
    mock_response = MagicMock()
    mock_response.text = '{"supported": true}'
    mock_client.models.generate_content.return_value = mock_response

    result = validate_answer_with_context(
        question="How does supervised learning work?",
        answer="It uses labeled examples to train a model.",
        context=(
            "Supervised learning uses labeled examples "
            "to train models."
        ),
    )

    assert result is True
    mock_client.models.generate_content.assert_called_once()


@patch("app.services.rag_service.client")
def test_validate_answer_with_context_rejects_unsupported_answer(
    mock_client,
):
    mock_response = MagicMock()
    mock_response.text = '{"supported": false}'
    mock_client.models.generate_content.return_value = mock_response

    result = validate_answer_with_context(
        question="What is the capital of Japan?",
        answer="The capital of Japan is Tokyo.",
        context="Supervised learning uses labeled examples.",
    )

    assert result is False


@patch("app.services.rag_service.client")
def test_validate_answer_with_context_rejects_invalid_json(
    mock_client,
):
    mock_response = MagicMock()
    mock_response.text = "This answer is supported."
    mock_client.models.generate_content.return_value = mock_response

    with pytest.raises(ValueError):
        validate_answer_with_context(
            question="Explain supervised learning",
            answer="It uses labeled examples.",
            context="Supervised learning uses labeled examples.",
        )


@patch("app.services.rag_service.client")
def test_validate_answer_with_context_propagates_api_error(
    mock_client,
):
    mock_client.models.generate_content.side_effect = RuntimeError(
        "Simulated Gemini validation failure"
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated Gemini validation failure",
    ):
        validate_answer_with_context(
            question="Explain supervised learning",
            answer="It uses labeled examples.",
            context="Supervised learning uses labeled examples.",
        )


# --------------------------------------------------
# End-to-end RAG service tests
# --------------------------------------------------

@patch("app.services.rag_service.validate_answer_with_context")
@patch("app.services.rag_service.generate_rag_answer")
@patch("app.services.embedding_service.embed_text")
def test_answer_question_returns_answer_and_sources(
    mock_embed_text,
    mock_generate_answer,
    mock_validate_answer,
):
    mock_embed_text.return_value = [0.1, 0.2, 0.3]
    mock_generate_answer.return_value = (
        "Supervised learning uses labeled data."
    )
    mock_validate_answer.return_value = True

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = RESULTS

    result = answer_question(
        "How does supervised learning work?",
        mock_vector_store,
    )

    assert result["answer"] == (
        "Supervised learning uses labeled data."
    )
    assert len(result["sources"]) == 2
    assert result["sources"][0]["chunk_id"] == "chunk_0001"

    mock_embed_text.assert_called_once()
    mock_vector_store.search.assert_called_once_with(
        [0.1, 0.2, 0.3],
        top_k=3,
    )
    mock_generate_answer.assert_called_once()
    mock_validate_answer.assert_called_once()


@patch("app.services.rag_service.validate_answer_with_context")
@patch("app.services.rag_service.generate_rag_answer")
@patch("app.services.embedding_service.embed_text")
def test_answer_question_replaces_unsupported_answer(
    mock_embed_text,
    mock_generate_answer,
    mock_validate_answer,
):
    mock_embed_text.return_value = [0.1, 0.2, 0.3]
    mock_generate_answer.return_value = (
        "The capital of Japan is Tokyo."
    )
    mock_validate_answer.return_value = False

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = RESULTS

    result = answer_question(
        "What is the capital of Japan?",
        mock_vector_store,
    )

    assert result["answer"] == UNSUPPORTED_ANSWER
    assert len(result["sources"]) == 2
    mock_validate_answer.assert_called_once()


@patch("app.services.rag_service.validate_answer_with_context")
@patch("app.services.rag_service.generate_rag_answer")
@patch("app.services.embedding_service.embed_text")
def test_answer_question_propagates_validation_failure(
    mock_embed_text,
    mock_generate_answer,
    mock_validate_answer,
):
    mock_embed_text.return_value = [0.1, 0.2, 0.3]
    mock_generate_answer.return_value = (
        "Supervised learning uses labeled data."
    )
    mock_validate_answer.side_effect = RuntimeError(
        "Simulated validation failure"
    )

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = RESULTS

    with pytest.raises(
        RuntimeError,
        match="Simulated validation failure",
    ):
        answer_question(
            "How does supervised learning work?",
            mock_vector_store,
        )


@patch("app.services.rag_service.client")
@patch("app.services.embedding_service.embed_text")
def test_answer_question_uses_unsupported_fallback(
    mock_embed,
    mock_client,
):
    mock_embed.return_value = [0.1, 0.2, 0.3]

    mock_response = MagicMock()
    mock_response.text = UNSUPPORTED_ANSWER
    mock_client.models.generate_content.return_value = mock_response

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = RESULTS

    result = answer_question(
        "What is the capital of Japan?",
        mock_vector_store,
    )

    assert result["answer"] == UNSUPPORTED_ANSWER
    assert len(result["sources"]) == 2

    # The generated fallback should not trigger another Gemini call.
    mock_client.models.generate_content.assert_called_once()


# --------------------------------------------------
# Retrieval and input validation tests
# --------------------------------------------------

@patch("app.services.embedding_service.embed_text")
def test_answer_question_reports_embedding_failure(mock_embed_text):
    mock_embed_text.side_effect = RuntimeError(
        "Simulated embedding failure"
    )

    mock_vector_store = MagicMock()

    with pytest.raises(
        RuntimeError,
        match="Simulated embedding failure",
    ):
        answer_question(
            "How does supervised learning work?",
            mock_vector_store,
        )

    mock_vector_store.search.assert_not_called()


@patch("app.services.embedding_service.embed_text")
def test_answer_question_reports_empty_retrieval(mock_embed_text):
    mock_embed_text.return_value = [0.1, 0.2, 0.3]

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = []

    with pytest.raises(
        ValueError,
        match="No relevant transcript chunks found",
    ):
        answer_question(
            "Explain an unrelated topic",
            mock_vector_store,
        )


def test_answer_question_rejects_empty_question():
    mock_vector_store = MagicMock()

    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        answer_question("   ", mock_vector_store)

    mock_vector_store.search.assert_not_called()


@patch("app.services.rag_service.client")
def test_validate_answer_with_context_accepts_markdown_wrapped_json(
    mock_client,
):
    mock_response = MagicMock()
    mock_response.text = (
        '```json\n{"supported": true}\n```'
    )
    mock_client.models.generate_content.return_value = mock_response

    result = validate_answer_with_context(
        question="How does supervised learning work?",
        answer="It uses labeled examples to train a model.",
        context="Supervised learning uses labeled examples to train models.",
    )

    assert result is True
    mock_client.models.generate_content.assert_called_once()
