
from unittest.mock import MagicMock, patch

from app.services.rag_service import (
    build_context,
    generate_rag_answer,
)


RESULTS = [
    {
        "text": (
            "Supervised learning uses labeled examples "
            "to train a model to make predictions on new data."
        ),
        "start": 8.0,
        "end": 16.0,
        "distance": 0.4,
    },
    {
        "text": (
            "Unsupervised learning works with unlabeled data "
            "and can discover hidden patterns or structures."
        ),
        "start": 16.0,
        "end": 24.0,
        "distance": 0.7,
    },
]


def test_build_context():
    context = build_context(RESULTS)

    assert isinstance(context, str)
    assert "Supervised learning" in context
    assert "Unsupervised learning" in context


@patch("app.services.rag_service.client")
def test_generate_rag_answer(mock_client):
    expected_answer = (
        "Supervised learning trains a model using labeled examples "
        "so it can make predictions on new data."
    )

    mock_response = MagicMock()
    mock_response.text = expected_answer
    mock_client.models.generate_content.return_value = mock_response

    question = "How does supervised learning work?"
    context = build_context(RESULTS)

    answer = generate_rag_answer(question, context)

    assert isinstance(answer, str)
    assert answer.strip() == expected_answer

    mock_client.models.generate_content.assert_called_once()
