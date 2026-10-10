
from app.services.rag_service import create_rag_chunks


test_segments = [
    {
        "text": "Machine learning allows computers to learn patterns from data.",
        "start": 0.0,
        "duration": 5.0,
    },
    {
        "text": "Supervised learning uses labeled examples to train models.",
        "start": 5.0,
        "duration": 5.0,
    },
    {
        "text": "The model learns from these examples and makes predictions.",
        "start": 10.0,
        "duration": 5.0,
    },
    {
        "text": "Unsupervised learning works with unlabeled data.",
        "start": 15.0,
        "duration": 5.0,
    },
]


def test_rag_chunks_have_unique_ids_and_valid_timestamps():
    chunks = create_rag_chunks(test_segments, max_chars=130)

    assert isinstance(chunks, list)
    assert len(chunks) > 0

    # Every chunk must contain non-empty text and valid timestamps.
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert chunk["chunk_id"]
        assert isinstance(chunk["text"], str)
        assert chunk["text"].strip()
        assert chunk["start"] < chunk["end"]

    # Every chunk must have a unique ID.
    chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))

    # IDs should follow the same order as the chunks.
    expected_ids = [
        f"chunk_{index:04d}"
        for index in range(1, len(chunks) + 1)
    ]
    assert chunk_ids == expected_ids


def test_empty_transcript_produces_no_chunks():
    assert create_rag_chunks([]) == []
