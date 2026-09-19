from app.services.summarizer_service import (
    create_summary_chunks,
    summarize_chunk,
    combine_chunk_summaries,
    generate_final_summary,
)


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
            "text": "It repeatedly divides the search space in half.",
            "start": 10,
            "duration": 5,
        },
    ]

    chunks = create_summary_chunks(
        segments,
        max_chars=60
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
            "summary": "It repeatedly divides the search space.",
        },
    ]

    combined = combine_chunk_summaries(
        chunk_summaries
    )

    assert "Chunk 1" in combined
    assert "Chunk 2" in combined
    assert "Binary search" in combined
    assert "divides the search space" in combined


def test_summarize_chunk():
    chunk = [
        {
            "id": 0,
            "text": "Binary search works on sorted arrays.",
            "start": 0,
            "duration": 5,
        },
        {
            "id": 1,
            "text": "It repeatedly divides the search space in half.",
            "start": 5,
            "duration": 5,
        },
    ]

    result = summarize_chunk(chunk)

    assert "start" in result
    assert "end" in result
    assert "summary" in result

    assert result["start"] == 0
    assert result["end"] == 10

    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


def test_generate_final_summary():
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

    print("\nGenerated structured summary:")
    print(result)