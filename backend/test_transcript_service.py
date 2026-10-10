
from types import SimpleNamespace
from unittest.mock import patch

from app.services.transcript_service import fetch_transcript


VIDEO_ID = "m2Jjbr380m0"



class FakeFetchedTranscript:
    def __init__(self, snippets, language, language_code, is_generated):
        self.snippets = snippets
        self.language = language
        self.language_code = language_code
        self.is_generated = is_generated

    def __iter__(self):
        return iter(self.snippets)


def make_transcript(language_code="te", is_generated=True):
    snippets = [
        SimpleNamespace(
            text="మొదటి భాగం",
            start=0.0,
            duration=2.0,
        ),
        SimpleNamespace(
            text="రెండవ భాగం",
            start=2.0,
            duration=3.0,
        ),
    ]

    return FakeFetchedTranscript(
        snippets=snippets,
        language="Telugu (auto-generated)",
        language_code=language_code,
        is_generated=is_generated,
    )


@patch("app.services.transcript_service.translate_batch")
@patch("app.services.transcript_service.YouTubeTranscriptApi")
def test_fetch_transcript_translates_and_preserves_timestamps(
    mock_api_class,
    mock_translate_batch,
):
    fetched = make_transcript()

    transcript = SimpleNamespace(
        is_generated=True,
        fetch=lambda: fetched,
    )

    mock_api_class.return_value.list.return_value = [transcript]

    mock_translate_batch.return_value = [
        {"id": 0, "translation": "First segment"},
        {"id": 1, "translation": "Second segment"},
    ]

    result = fetch_transcript(VIDEO_ID)

    assert result["language_code"] == "te"
    assert result["is_generated"] is True
    assert len(result["original_segments"]) == 2
    assert len(result["english_segments"]) == 2

    assert result["english_segments"][0] == {
        "text": "First segment",
        "start": 0.0,
        "duration": 2.0,
    }
    assert result["english_segments"][1] == {
        "text": "Second segment",
        "start": 2.0,
        "duration": 3.0,
    }

    mock_translate_batch.assert_called_once()


@patch("app.services.transcript_service.YouTubeTranscriptApi")
def test_fetch_transcript_raises_when_no_transcript_exists(
    mock_api_class,
):
    mock_api_class.return_value.list.return_value = []

    try:
        fetch_transcript(VIDEO_ID)
    except ValueError as exc:
        assert str(exc) == "No transcript available for this video"
    else:
        raise AssertionError("Expected ValueError for missing transcript")
