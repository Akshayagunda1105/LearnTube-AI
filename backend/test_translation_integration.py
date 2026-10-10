
from types import SimpleNamespace
from unittest.mock import patch

from app.services.transcript_service import fetch_transcript


VIDEO_ID = "m2Jjbr380m0"


@patch("app.services.transcript_service.translate_batch")
@patch("app.services.transcript_service.YouTubeTranscriptApi")
def test_transcript_translation_integration(
    mock_api_class,
    mock_translate_batch,
):
    # Simulate three transcript segments.
    snippets = [
        SimpleNamespace(text="మొదటి భాగం", start=0.0, duration=2.0),
        SimpleNamespace(text="రెండవ భాగం", start=2.0, duration=3.0),
        SimpleNamespace(text="మూడవ భాగం", start=5.0, duration=2.5),
    ]

    class FakeFetchedTranscript(list):
        def __init__(self, items):
            super().__init__(items)
            self.language = "Telugu"
            self.language_code = "te"
            self.is_generated = True

    fetched = FakeFetchedTranscript(snippets)

    transcript = SimpleNamespace(
        is_generated=True,
        fetch=lambda: fetched,
    )

    mock_api_class.return_value.list.return_value = [transcript]

    mock_translate_batch.return_value = [
        {"id": 0, "translation": "First segment"},
        {"id": 1, "translation": "Second segment"},
        {"id": 2, "translation": "Third segment"},
    ]

    result = fetch_transcript(VIDEO_ID)

    original = result["original_segments"]
    english = result["english_segments"]

    assert result["language"] == "Telugu"
    assert result["language_code"] == "te"
    assert len(original) == 3
    assert len(english) == 3

    for index in range(3):
        assert english[index]["text"] == f"{['First', 'Second', 'Third'][index]} segment"
        assert english[index]["start"] == original[index]["start"]
        assert english[index]["duration"] == original[index]["duration"]

    mock_api_class.return_value.list.assert_called_once_with(VIDEO_ID)
    mock_translate_batch.assert_called_once()
