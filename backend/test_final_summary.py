
from unittest.mock import MagicMock, patch

from app.services.summarizer_service import (
    combine_chunk_summaries,
    generate_final_summary,
)


def test_combine_chunk_summaries():
    chunk_summaries = [
        {
            "start": 0.0,
            "end": 60.0,
            "summary": "Machine learning allows computers to learn patterns from data.",
        },
        {
            "start": 60.0,
            "end": 120.0,
            "summary": "Supervised learning uses labeled examples to train predictive models.",
        },
        {
            "start": 120.0,
            "end": 180.0,
            "summary": "Unsupervised learning discovers patterns in unlabeled data.",
        },
    ]

    combined = combine_chunk_summaries(chunk_summaries)

    assert isinstance(combined, str)
    assert len(combined.strip()) > 0
    assert "Machine learning" in combined
    assert "Supervised learning" in combined
    assert "Unsupervised learning" in combined


@patch("app.services.summarizer_service.client")
def test_generate_final_summary(mock_client):
    expected_summary = {
        "overview": "Machine learning identifies patterns in data.",
        "key_points": [
            "Supervised learning uses labeled data.",
            "Unsupervised learning finds hidden patterns.",
        ],
        "concepts": [
            {
                "title": "Supervised learning",
                "explanation": "A model learns from labeled examples.",
            }
        ],
        "takeaways": [
            "Choose a learning approach based on the problem."
        ],
    }

    mock_response = MagicMock()
    mock_response.text = __import__("json").dumps(expected_summary)

    mock_client.models.generate_content.return_value = mock_response

    result = generate_final_summary(
        "Machine learning learns patterns from data."
    )

    assert isinstance(result, dict)
    assert result["overview"] == expected_summary["overview"]
    assert len(result["key_points"]) == 2

    mock_client.models.generate_content.assert_called_once()
