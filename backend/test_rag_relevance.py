
from app.services.vector_store import VectorStore


EVALUATION_CHUNKS = [
    {
        "chunk_id": "chunk_supervised",
        "text": "Supervised learning uses labeled examples to train models.",
        "start": 0.0,
        "end": 8.0,
        "embedding": [1.0, 0.0, 0.0],
    },
    {
        "chunk_id": "chunk_unsupervised",
        "text": "Unsupervised learning discovers patterns in unlabeled data.",
        "start": 8.0,
        "end": 16.0,
        "embedding": [0.0, 1.0, 0.0],
    },
]


EVALUATION_CASES = [
    {
        "question": "How does supervised learning work?",
        "query_embedding": [0.95, 0.05, 0.0],
        "expected_chunk_id": "chunk_supervised",
        "answerable_from_dataset": True,
    },
    {
        "question": "What is unsupervised learning?",
        "query_embedding": [0.05, 0.95, 0.0],
        "expected_chunk_id": "chunk_unsupervised",
        "answerable_from_dataset": True,
    },
    {
        "question": "What is the capital of Japan?",
        "query_embedding": [0.0, 0.0, 1.0],
        "expected_chunk_id": None,
        "answerable_from_dataset": False,
    },
]


def test_evaluation_dataset_has_answerable_and_unsupported_questions():
    assert any(
        case["answerable_from_dataset"]
        for case in EVALUATION_CASES
    )
    assert any(
        not case["answerable_from_dataset"]
        for case in EVALUATION_CASES
    )


def test_retrieval_ranks_expected_chunks_for_answerable_questions():
    store = VectorStore(dimension=3)
    store.add_chunks(EVALUATION_CHUNKS)

    for case in EVALUATION_CASES:
        if not case["answerable_from_dataset"]:
            continue

        results = store.search(case["query_embedding"], top_k=1)

        assert results[0]["chunk_id"] == case["expected_chunk_id"]


def test_unsupported_question_still_gets_nearest_chunk_from_faiss():
    store = VectorStore(dimension=3)
    store.add_chunks(EVALUATION_CHUNKS)

    unsupported_case = next(
        case
        for case in EVALUATION_CASES
        if not case["answerable_from_dataset"]
    )

    results = store.search(
        unsupported_case["query_embedding"],
        top_k=1,
    )

    # FAISS returns a nearest neighbor even though the
    # evaluation dataset marks this question unsupported.
    assert len(results) == 1
    assert results[0]["chunk_id"] in {
        "chunk_supervised",
        "chunk_unsupervised",
    }
