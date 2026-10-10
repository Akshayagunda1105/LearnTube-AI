
from types import SimpleNamespace
from unittest.mock import patch

from app.services.translation_service import create_batches
from app.services.transcript_service import fetch_transcript


VIDEO_ID = "m2Jjbr380m0"


@patch("app.services.transcript_service.translate_batch")
@patch("app.services.transcript_service.YouTubeTranscriptApi")
def test_transcript_translation_preserves_timestamps(
    mock_api_class,
    mock_translate_batch,
):
    # Fake four Telugu transcript segments.
    snippets = [
        SimpleNamespace(text="మొదటి భాగం", start=0.0, duration=2.0),
        SimpleNamespace(text="రెండవ భాగం", start=2.0, duration=3.0),
        SimpleNamespace(text="మూడవ భాగం", start=5.0, duration=2.5),
        SimpleNamespace(text="నాలుగవ భాగం", start=7.5, duration=2.0),
    ]

    class FakeFetchedTranscript(list):
        def __init__(self, snippets):
            super().__init__(snippets)
            self.language = "Telugu"
            self.language_code = "te"
            self.is_generated = True


    fetched = FakeFetchedTranscript(snippets)

    transcript = SimpleNamespace(
        language_code="te",
        is_generated=True,
        fetch=lambda: fetched,
    )

    mock_api_class.return_value.list.return_value = [transcript]

    mock_translate_batch.return_value = [
        {"id": 0, "translation": "First segment"},
        {"id": 1, "translation": "Second segment"},
        {"id": 2, "translation": "Third segment"},
        {"id": 3, "translation": "Fourth segment"},
    ]

    result = fetch_transcript(VIDEO_ID)

    original = result["original_segments"]
    english = result["english_segments"]

    assert len(original) == 4
    assert len(english) == 4

    for index in range(4):
        assert english[index]["start"] == original[index]["start"]
        assert english[index]["duration"] == original[index]["duration"]

    assert english[0]["text"] == "First segment"
    assert english[3]["text"] == "Fourth segment"
    mock_translate_batch.assert_called_once()


def test_create_batches_for_transcript_segments():
    segments = [
        {"text": "First segment", "start": 0.0, "duration": 2.0},
        {"text": "Second segment", "start": 2.0, "duration": 3.0},
    ]

    batches = create_batches(segments, max_chars=6000)

    assert len(batches) >= 1
    assert sum(len(batch) for batch in batches) == len(segments)
