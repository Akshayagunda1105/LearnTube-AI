from app.services.notes_service import (
    create_note_chunks,
    generate_chunk_notes,
    combine_note_sections,
)


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


def test_generate_chunk_notes(monkeypatch):
    chunk = [
        {
            "id": 0,
            "text": "Supervised learning uses labeled data.",
            "start": 120,
            "duration": 5,
        },
        {
            "id": 1,
            "text": "The model learns relationships between inputs and labels.",
            "start": 125,
            "duration": 5,
        },
    ]

    class FakeResponse:
        text = """
        {
            "title": "Supervised Learning",
            "points": [
                "Uses labeled data.",
                "Learns relationships between inputs and labels."
            ]
        }
        """

    def mock_generate_content(model, contents):
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.notes_service.client.models.generate_content",
        mock_generate_content,
    )

    result = generate_chunk_notes(chunk)

    assert isinstance(result, dict)

    assert result["title"] == "Supervised Learning"

    assert result["timestamp"] == 120

    assert isinstance(result["points"], list)
    assert len(result["points"]) == 2


def test_generate_chunk_notes_uses_first_segment_timestamp(
    monkeypatch
):
    chunk = [
        {
            "id": 10,
            "text": "First concept.",
            "start": 45.5,
            "duration": 4,
        },
        {
            "id": 11,
            "text": "Second concept.",
            "start": 49.5,
            "duration": 4,
        },
    ]

    class FakeResponse:
        text = """
        {
            "title": "Test Topic",
            "points": [
                "Important point."
            ]
        }
        """

    def mock_generate_content(model, contents):
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.notes_service.client.models.generate_content",
        mock_generate_content,
    )

    result = generate_chunk_notes(chunk)

    assert result["timestamp"] == 45.5


def test_generate_chunk_notes_rejects_invalid_json(
    monkeypatch
):
    chunk = [
        {
            "id": 0,
            "text": "Some educational content.",
            "start": 10,
            "duration": 5,
        }
    ]

    class FakeResponse:
        text = "This is not valid JSON."

    def mock_generate_content(model, contents):
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.notes_service.client.models.generate_content",
        mock_generate_content,
    )

    try:
        generate_chunk_notes(chunk)
        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == "Gemini returned invalid JSON"


def test_generate_chunk_notes_rejects_missing_points(
    monkeypatch
):
    chunk = [
        {
            "id": 0,
            "text": "Some educational content.",
            "start": 10,
            "duration": 5,
        }
    ]

    class FakeResponse:
        text = """
        {
            "title": "Some Topic"
        }
        """

    def mock_generate_content(model, contents):
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.notes_service.client.models.generate_content",
        mock_generate_content,
    )

    try:
        generate_chunk_notes(chunk)
        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == (
            "Notes are missing required field: points"
        )


def test_generate_chunk_notes_rejects_empty_chunk():
    try:
        generate_chunk_notes([])
        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == "Chunk cannot be empty"


def test_combine_note_sections():
    note_sections = [
        {
            "title": "Machine Learning",
            "timestamp": 0,
            "points": [
                "Machine learning allows systems to learn from data."
            ],
        },
        {
            "title": "Supervised Learning",
            "timestamp": 120,
            "points": [
                "Supervised learning uses labeled data."
            ],
        },
    ]

    result = combine_note_sections(note_sections)

    assert isinstance(result, dict)
    assert "sections" in result

    assert len(result["sections"]) == 2

    assert (
        result["sections"][0]["title"]
        == "Machine Learning"
    )

    assert (
        result["sections"][1]["title"]
        == "Supervised Learning"
    )


def test_combine_note_sections_preserves_order():
    note_sections = [
        {
            "title": "First Topic",
            "timestamp": 100,
            "points": ["First point."],
        },
        {
            "title": "Second Topic",
            "timestamp": 200,
            "points": ["Second point."],
        },
        {
            "title": "Third Topic",
            "timestamp": 300,
            "points": ["Third point."],
        },
    ]

    result = combine_note_sections(note_sections)

    timestamps = [
        section["timestamp"]
        for section in result["sections"]
    ]

    assert timestamps == [100, 200, 300]


def test_combine_note_sections_rejects_empty_sections():
    try:
        combine_note_sections([])

        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == (
            "Note sections cannot be empty"
        )


def test_combine_note_sections_rejects_missing_field():
    note_sections = [
        {
            "title": "Machine Learning",
            "timestamp": 0,
        }
    ]

    try:
        combine_note_sections(note_sections)

        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == (
            "Note section is missing required field: points"
        )