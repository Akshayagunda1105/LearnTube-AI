
import os

import pytest

from app.services.embedding_service import embed_chunks, embed_text
from app.services.vector_store import VectorStore


@pytest.mark.skipif(
    os.getenv("RUN_REAL_RAG_TEST") != "1",
    reason="Live Gemini API retrieval test is opt-in.",
)
def test_real_rag_retrieval():
    chunks = [
        {
            "text": (
                "Machine learning is a field of artificial intelligence "
                "that allows computers to learn patterns from data."
            ),
            "start": 0.0,
            "end": 8.0,
        },
        {
            "text": (
                "Supervised learning uses labeled examples to train a "
                "model to make predictions on new data."
            ),
            "start": 8.0,
            "end": 16.0,
        },
        {
            "text": (
                "Unsupervised learning works with unlabeled data and "
                "can discover hidden patterns or structures."
            ),
            "start": 16.0,
            "end": 24.0,
        },
    ]

    embedded_chunks = embed_chunks(chunks)

    dimension = len(embedded_chunks[0]["embedding"])
    store = VectorStore(dimension=dimension)
    store.add_chunks(embedded_chunks)

    question_embedding = embed_text(
        "How does supervised learning work?"
    )

    results = store.search(question_embedding, top_k=2)

    assert len(results) == 2
    assert results[0]["text"] == chunks[1]["text"]
    assert results[0]["start"] == 8.0
    assert results[0]["end"] == 16.0
