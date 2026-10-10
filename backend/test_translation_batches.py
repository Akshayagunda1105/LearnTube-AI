
from unittest.mock import patch

from app.services.translation_service import create_batches, translate_batch


def test_create_batches_splits_segments_by_character_limit():
    segments = [
        {"text": "First segment text.", "start": 0.0, "duration": 2.0},
        {"text": "Second segment text.", "start": 2.0, "duration": 2.5},
        {"text": "Third segment text.", "start": 4.5, "duration": 3.0},
        {"text": "Fourth segment text.", "start": 7.5, "duration": 2.0},
    ]

    batches = create_batches(segments, max_chars=25)

    assert len(batches) > 1
    assert sum(len(batch) for batch in batches) == len(segments)

    # Every segment must appear exactly once and in its original order.
    batched_segments = [segment for batch in batches for segment in batch]

    assert len(batched_segments) == len(segments)

    for index, segment in enumerate(batched_segments):
        assert segment["id"] == index
        assert segment["text"] == segments[index]["text"]
        assert segment["start"] == segments[index]["start"]
        assert segment["duration"] == segments[index]["duration"]

@patch("app.services.translation_service.client.models.generate_content")
def test_translate_batch_returns_validated_translations(mock_generate):
    mock_generate.return_value.text = (
        '[{"id": 0, "translation": "First translated segment"}, '
        '{"id": 1, "translation": "Second translated segment"}]'
    )

    batch = [
        {"id": 0, "text": "First transcript segment.", "start": 0.0, "duration": 2.0},
        {"id": 1, "text": "Second transcript segment.", "start": 2.0, "duration": 2.5},
    ]

    result = translate_batch(batch, "English")

    assert len(result) == 2
    assert result[0]["id"] == 0
    assert result[0]["translation"] == "First translated segment"
    assert result[1]["id"] == 1
    assert result[1]["translation"] == "Second translated segment"
    mock_generate.assert_called_once()
