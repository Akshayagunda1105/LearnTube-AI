from app.services.notes_service import create_note_chunks


def test_create_note_chunks():
    segments = [
        {
            "text": "Machine learning is a field of artificial intelligence.",
            "start": 0,
            "duration": 5,
        },
        {
            "text": "It allows machines to learn from data.",
            "start": 5,
            "duration": 5,
        },
        {
            "text": "Supervised learning uses labeled data.",
            "start": 10,
            "duration": 5,
        },
        {
            "text": "Unsupervised learning works with unlabeled data.",
            "start": 15,
            "duration": 5,
        },
    ]

    chunks = create_note_chunks(
        segments,
        max_chars=100
    )

    assert len(chunks) >= 1

    for chunk in chunks:
        assert len(chunk) > 0

        for segment in chunk:
            assert "id" in segment
            assert "text" in segment
            assert "start" in segment
            assert "duration" in segment


def test_note_chunks_preserve_segment_order():
    segments = [
        {
            "text": "First segment.",
            "start": 0,
            "duration": 2,
        },
        {
            "text": "Second segment.",
            "start": 2,
            "duration": 2,
        },
        {
            "text": "Third segment.",
            "start": 4,
            "duration": 2,
        },
    ]

    chunks = create_note_chunks(
        segments,
        max_chars=100
    )

    flattened_segments = [
        segment
        for chunk in chunks
        for segment in chunk
    ]

    assert [segment["id"] for segment in flattened_segments] == [
        0,
        1,
        2,
    ]


def test_note_chunks_preserve_timestamps():
    segments = [
        {
            "text": "First concept.",
            "start": 10.5,
            "duration": 3.2,
        },
        {
            "text": "Second concept.",
            "start": 13.7,
            "duration": 4.1,
        },
    ]

    chunks = create_note_chunks(
        segments,
        max_chars=100
    )

    assert chunks[0][0]["start"] == 10.5
    assert chunks[0][0]["duration"] == 3.2

    assert chunks[0][1]["start"] == 13.7
    assert chunks[0][1]["duration"] == 4.1


def test_large_segment_is_not_split():
    segments = [
        {
            "text": "A" * 150,
            "start": 0,
            "duration": 10,
        },
        {
            "text": "Small segment.",
            "start": 10,
            "duration": 3,
        },
    ]

    chunks = create_note_chunks(
        segments,
        max_chars=100
    )

    assert len(chunks) == 2

    assert chunks[0][0]["text"] == "A" * 150
    assert chunks[1][0]["text"] == "Small segment."