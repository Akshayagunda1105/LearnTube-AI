
import pytest

from app.services.vector_store import VectorStore


chunks = [
    {
        "chunk_id": "chunk_0001",
        "text": "Machine learning allows computers to learn patterns from data.",
        "start": 0.0,
        "end": 5.0,
        "embedding": [1.0, 0.0, 0.0],
    },
    {
        "chunk_id": "chunk_0002",
        "text": "Supervised learning uses labeled examples to train models.",
        "start": 5.0,
        "end": 10.0,
        "embedding": [0.0, 1.0, 0.0],
    },
    {
        "chunk_id": "chunk_0003",
        "text": "Unsupervised learning discovers patterns in unlabeled data.",
        "start": 10.0,
        "end": 15.0,
        "embedding": [0.9, 0.1, 0.0],
    },
]


def test_vector_store_retrieves_closest_chunks_with_ids():
    store = VectorStore(dimension=3)
    store.add_chunks(chunks)

    assert store.index.ntotal == 3
    assert len(store.chunks) == 3

    results = store.search([0.88, 0.12, 0.0], top_k=2)

    assert len(results) == 2

    # The third chunk is closest to the query vector.
    assert results[0]["chunk_id"] == "chunk_0003"
    assert results[0]["text"] == chunks[2]["text"]
    assert results[0]["start"] == 10.0
    assert results[0]["end"] == 15.0

    assert results[0]["distance"] < results[1]["distance"]

    # Retrieved distances must be ordinary Python floats.
    assert isinstance(results[0]["distance"], float)


def test_empty_chunks_are_rejected():
    store = VectorStore(dimension=3)

    with pytest.raises(ValueError, match="Chunks cannot be empty"):
        store.add_chunks([])


def test_search_on_empty_vector_store_is_rejected():
    store = VectorStore(dimension=3)

    with pytest.raises(ValueError, match="Vector store is empty"):
        store.search([1.0, 0.0, 0.0])


def test_embedding_dimension_mismatch_is_rejected():
    store = VectorStore(dimension=3)

    invalid_chunks = [
        {
            "text": "Example chunk",
            "start": 0.0,
            "end": 5.0,
            "embedding": [1.0, 0.0],
        }
    ]

    with pytest.raises(
        ValueError,
        match="Embedding dimension does not match",
    ):
        store.add_chunks(invalid_chunks)


def test_query_embedding_dimension_mismatch_is_rejected():
    store = VectorStore(dimension=3)
    store.add_chunks(chunks)

    with pytest.raises(
        ValueError,
        match="Query embedding dimension does not match",
    ):
        store.search([1.0, 0.0])


def test_vector_store_returns_closest_chunk_even_when_far_away():
    store = VectorStore(dimension=3)

    store.add_chunks(
        [
            {
                "chunk_id": "chunk_0001",
                "text": "A video about cooking recipes.",
                "start": 0.0,
                "end": 5.0,
                "embedding": [100.0, 0.0, 0.0],
            },
            {
                "chunk_id": "chunk_0002",
                "text": "A video about gardening.",
                "start": 5.0,
                "end": 10.0,
                "embedding": [0.0, 100.0, 0.0],
            },
        ]
    )

    # The query is far from both stored vectors.
    results = store.search([0.0, 0.0, 1.0], top_k=1)

    assert len(results) == 1

    # FAISS still returns a nearest neighbor.
    assert results[0]["chunk_id"] == "chunk_0001"

    # The returned distance exposes how far the
    # query is from that nearest neighbor.
    assert results[0]["distance"] == pytest.approx(10001.0)

def test_vector_store_orders_relevant_candidate_before_distant_candidate():
    store = VectorStore(dimension=3)

    store.add_chunks(
        [
            {
                "chunk_id": "candidate_close",
                "text": "Supervised learning uses labeled examples.",
                "start": 0.0,
                "end": 5.0,
                "embedding": [0.9, 0.1, 0.0],
            },
            {
                "chunk_id": "candidate_far",
                "text": "A recipe explains how to bake bread.",
                "start": 5.0,
                "end": 10.0,
                "embedding": [0.0, 0.0, 10.0],
            },
        ]
    )

    results = store.search([1.0, 0.0, 0.0], top_k=2)

    assert len(results) == 2
    assert results[0]["chunk_id"] == "candidate_close"
    assert results[1]["chunk_id"] == "candidate_far"
    assert results[0]["distance"] < results[1]["distance"]
