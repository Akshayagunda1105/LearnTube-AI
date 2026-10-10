from app.services.embedding_service import (
    embed_chunks,
)
from app.services.vector_store import VectorStore
from app.services.rag_service import answer_question


print("Complete RAG pipeline test")
print("-" * 60)


# --------------------------------------------------
# Create transcript chunks
# --------------------------------------------------

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


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

print("Generating transcript embeddings...")

embedded_chunks = embed_chunks(
    chunks
)

dimension = len(
    embedded_chunks[0]["embedding"]
)

print(
    "Embedding dimensions:",
    dimension
)


# --------------------------------------------------
# Create and populate vector store
# --------------------------------------------------

store = VectorStore(
    dimension=dimension
)

store.add_chunks(
    embedded_chunks
)

print(
    "Vectors stored:",
    store.index.ntotal
)


# --------------------------------------------------
# Ask a question
# --------------------------------------------------

question = (
    "How does supervised learning work?"
)

print("\nQuestion:")
print(question)


# --------------------------------------------------
# Run complete RAG pipeline
# --------------------------------------------------

print("\nRunning RAG pipeline...")
print("-" * 60)

result = answer_question(
    question,
    store,
    top_k=2
)


# --------------------------------------------------
# Display answer
# --------------------------------------------------

print("\nAnswer")
print("-" * 60)

print(result["answer"])


# --------------------------------------------------
# Display sources
# --------------------------------------------------

print("\nSources")
print("-" * 60)

for index, source in enumerate(
    result["sources"],
    start=1
):

    print(f"\nSource {index}")

    print(
        "Start:",
        source["start"]
    )

    print(
        "End:",
        source["end"]
    )

    print(
        "Distance:",
        source["distance"]
    )

    print(
        "Text:",
        source["text"]
    )


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert isinstance(result, dict)

assert "answer" in result
assert "sources" in result

assert isinstance(
    result["answer"],
    str
)

assert len(
    result["answer"].strip()
) > 0

assert len(
    result["sources"]
) == 2

# The supervised-learning chunk should be
# the most relevant source.

assert (
    result["sources"][0]["text"]
    == chunks[1]["text"]
)

assert (
    result["sources"][0]["start"]
    == 8.0
)

assert (
    result["sources"][0]["end"]
    == 16.0
)


print("\n" + "-" * 60)
print("Complete RAG pipeline test passed successfully!")