from app.services.vector_store import VectorStore


print("Vector store test")
print("-" * 60)


# --------------------------------------------------
# Create sample embedded chunks
# --------------------------------------------------

chunks = [
    {
        "text": "Machine learning allows computers to learn patterns from data.",
        "start": 0.0,
        "end": 5.0,
        "embedding": [1.0, 0.0, 0.0],
    },
    {
        "text": "Supervised learning uses labeled examples to train models.",
        "start": 5.0,
        "end": 10.0,
        "embedding": [0.0, 1.0, 0.0],
    },
    {
        "text": "Unsupervised learning discovers patterns in unlabeled data.",
        "start": 10.0,
        "end": 15.0,
        "embedding": [0.9, 0.1, 0.0],
    },
]


# --------------------------------------------------
# Create vector store
# --------------------------------------------------

store = VectorStore(
    dimension=3
)


print("FAISS dimension:", store.dimension)
print("Initial vectors:", store.index.ntotal)


# --------------------------------------------------
# Add chunks
# --------------------------------------------------

store.add_chunks(chunks)


print("Vectors after adding:", store.index.ntotal)
print("Stored chunks:", len(store.chunks))


assert store.index.ntotal == 3
assert len(store.chunks) == 3


# --------------------------------------------------
# Search
# --------------------------------------------------

query_embedding = [
    0.88,
    0.12,
    0.0,
]


results = store.search(
    query_embedding,
    top_k=2
)


print("\nSearch results")
print("-" * 60)


for index, result in enumerate(
    results,
    start=1
):

    print(f"\nResult {index}")
    print("Text:", result["text"])
    print("Start:", result["start"])
    print("End:", result["end"])
    print("Distance:", result["distance"])


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert len(results) == 2

# The unsupervised learning chunk has embedding
# [0.9, 0.1, 0.0], which should be closest
# to the query [0.88, 0.12, 0.0].

assert results[0]["text"] == (
    "Unsupervised learning discovers patterns "
    "in unlabeled data."
)

assert results[0]["start"] == 10.0
assert results[0]["end"] == 15.0

assert results[0]["distance"] < results[1]["distance"]


print("\n" + "-" * 60)
print("Vector store test passed successfully!")