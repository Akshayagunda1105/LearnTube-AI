
import os

import pytest

from app.services.embedding_service import embed_text, embed_chunks


@pytest.mark.skipif(
    os.getenv("RUN_REAL_RAG_TEST") != "1",
    reason="Live Gemini API test is opt-in.",
)
def test_embedding_service():
    text = (
        "Machine learning allows computers to learn "
        "patterns from data."
    )

    embedding = embed_text(text)

    assert isinstance(embedding, list)
    assert len(embedding) > 0

    chunks = [
        {
            "text": (
                "Machine learning allows computers "
                "to learn patterns from data."
            ),
            "start": 0.0,
            "end": 5.0,
        },
        {
            "text": (
                "Supervised learning uses labeled "
                "examples to train predictive models."
            ),
            "start": 5.0,
            "end": 10.0,
        },
    ]

    embedded_chunks = embed_chunks(chunks)

    assert len(embedded_chunks) == len(chunks)

    for original, embedded in zip(chunks, embedded_chunks):
        assert embedded["text"] == original["text"]
        assert embedded["start"] == original["start"]
        assert embedded["end"] == original["end"]
        assert isinstance(embedded["embedding"], list)
        assert len(embedded["embedding"]) > 0
