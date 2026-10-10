
import json

import pytest
from pydantic import ValidationError

from app.services.summarizer_service import (
    FinalSummary,
    SummaryChunk,
    create_summary_chunks,
    summarize_chunk,
    combine_chunk_summaries,
    generate_final_summary,
)


VALID_SUMMARY = {
    "overview": "The video explains binary search.",
    "key_points": [
        "Binary search works on sorted arrays.",
        "It repeatedly divides the search space in half.",
    ],
    "concepts": [
        {
            "title": "Binary Search",
            "explanation": (
                "A searching algorithm that halves "
                "the search space."
            ),
        }
    ],
    "takeaways": [
        "The input array must be sorted."
    ],
}


def test_create_summary_chunks():
    segments = [
        {
            "text": "Binary search is a searching algorithm.",
            "start": 0,
            "duration": 5,
        },
        {
            "text": "It works on sorted arrays.",
            "start": 5,
            "duration": 5,
        },
        {
            "text": (
                "It repeatedly divides the search space in half."
            ),
            "start": 10,
            "duration": 5,
        },
    ]

    chunks = create_summary_chunks(
        segments,
        max_chars=60,
    )

    assert len(chunks) >= 1

    for chunk in chunks:
        assert len(chunk) > 0

        for segment in chunk:
            assert "id" in segment
            assert "text" in segment
            assert "start" in segment
            assert "duration" in segment


def test_combine_chunk_summaries():
    chunk_summaries = [
        {
            "start": 0,
            "end": 10,
            "summary": "Binary search works on sorted arrays.",
        },
        {
            "start": 10,
            "end": 20,
            "summary": (
                "It repeatedly divides the search space."
            ),
        },
    ]

    combined = combine_chunk_summaries(
        chunk_summaries
    )

    assert "Chunk 1" in combined
    assert "Chunk 2" in combined
    assert "Binary search" in combined
    assert "divides the search space" in combined


def test_summarize_chunk(monkeypatch):
    chunk = [
        {
            "id": 0,
            "text": "Binary search works on sorted arrays.",
            "start": 0,
            "duration": 5,
        },
        {
            "id": 1,
            "text": (
                "It repeatedly divides the search space in half."
            ),
            "start": 5,
            "duration": 5,
        },
    ]

    class FakeResponse:
        text = (
            "Binary search works on sorted arrays "
            "and repeatedly halves the search space."
        )

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(
        "app.services.summarizer_service.client",
        FakeClient(),
    )

    result = summarize_chunk(chunk)

    assert "start" in result
    assert "end" in result
    assert "summary" in result

    assert result["start"] == 0
    assert result["end"] == 10

    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


def test_generate_final_summary(monkeypatch):
    combined_summaries = """
Chunk 1
Start: 0
End: 10

Summary:
Binary search works on sorted arrays.

Chunk 2
Start: 10
End: 20

Summary:
It repeatedly divides the search space in half.
"""

    class FakeResponse:
        text = json.dumps(VALID_SUMMARY)

    class FakeModels:
        def generate_content(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(
        "app.services.summarizer_service.client",
        FakeClient(),
    )

    result = generate_final_summary(
        combined_summaries
    )

    assert isinstance(result, dict)

    assert "overview" in result
    assert "key_points" in result
    assert "concepts" in result
    assert "takeaways" in result

    assert isinstance(result["overview"], str)
    assert len(result["overview"].strip()) > 0

    assert isinstance(result["key_points"], list)
    assert isinstance(result["concepts"], list)
    assert isinstance(result["takeaways"], list)

    for concept in result["concepts"]:
        assert "title" in concept
        assert "explanation" in concept

    assert result == VALID_SUMMARY


# Pydantic validation tests

def test_valid_summary_is_accepted():
    summary = FinalSummary.model_validate(
        VALID_SUMMARY
    )

    assert summary.overview == VALID_SUMMARY["overview"]
    assert len(summary.key_points) == 2
    assert summary.concepts[0].title == "Binary Search"


def test_missing_required_field_is_rejected():
    invalid_summary = VALID_SUMMARY.copy()
    del invalid_summary["overview"]

    with pytest.raises(ValidationError):
        FinalSummary.model_validate(
            invalid_summary
        )


def test_wrong_field_type_is_rejected():
    invalid_summary = {
        **VALID_SUMMARY,
        "key_points": [123],
    }

    with pytest.raises(ValidationError):
        FinalSummary.model_validate(
            invalid_summary
        )


def test_empty_concept_title_is_rejected():
    invalid_summary = json.loads(
        json.dumps(VALID_SUMMARY)
    )
    invalid_summary["concepts"][0]["title"] = "   "

    with pytest.raises(ValidationError):
        FinalSummary.model_validate(
            invalid_summary
        )


def test_malformed_json_is_rejected():
    malformed_json = '{"overview": "Incomplete JSON"'

    with pytest.raises(ValidationError):
        FinalSummary.model_validate_json(
            malformed_json
        )


def test_invalid_timestamp_order_is_rejected():
    with pytest.raises(ValidationError):
        SummaryChunk(
            start=120,
            end=90,
            summary="A sample summary.",
        )


def test_empty_key_points_are_rejected():
    invalid_summary = {
        **VALID_SUMMARY,
        "key_points": [],
    }

    with pytest.raises(ValidationError):
        FinalSummary.model_validate(
            invalid_summary
        )


def test_empty_concepts_are_rejected():
    invalid_summary = {
        **VALID_SUMMARY,
        "concepts": [],
    }

    with pytest.raises(ValidationError):
        FinalSummary.model_validate(
            invalid_summary
        )


def test_empty_takeaways_are_rejected():
    invalid_summary = {
        **VALID_SUMMARY,
        "takeaways": [],
    }

    with pytest.raises(ValidationError):
        FinalSummary.model_validate(
            invalid_summary
        )

def test_generate_final_summary_retries_after_invalid_output(monkeypatch):
    responses = [
        '{"overview": "Incomplete JSON"',
        json.dumps(VALID_SUMMARY),
    ]

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModels:
        def __init__(self):
            self.calls = 0

        def generate_content(self, **kwargs):
            response_text = responses[self.calls]
            self.calls += 1
            return FakeResponse(response_text)

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    fake_client = FakeClient()

    monkeypatch.setattr(
        "app.services.summarizer_service.client",
        fake_client,
    )

    result = generate_final_summary(
        "Binary search works on sorted arrays."
    )

    assert result == VALID_SUMMARY
    assert fake_client.models.calls == 2


def test_generate_final_summary_fails_after_max_retries(monkeypatch):
    class FakeResponse:
        text = '{"overview": "Incomplete JSON"'

    class FakeModels:
        def __init__(self):
            self.calls = 0

        def generate_content(self, **kwargs):
            self.calls += 1
            return FakeResponse()

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    fake_client = FakeClient()

    monkeypatch.setattr(
        "app.services.summarizer_service.client",
        fake_client,
    )

    with pytest.raises(
        ValueError,
        match="Could not generate a valid study summary",
    ):
        generate_final_summary(
            "Binary search works on sorted arrays."
        )

    assert fake_client.models.calls == 2


def test_gemini_schema_excludes_additional_properties():
    from app.services.summarizer_service import (
        FinalSummary,
        make_gemini_schema,
    )

    schema = make_gemini_schema(FinalSummary)

    def check_schema(value):
        if isinstance(value, dict):
            assert "additionalProperties" not in value
            for child in value.values():
                check_schema(child)
        elif isinstance(value, list):
            for child in value:
                check_schema(child)

    check_schema(schema)
