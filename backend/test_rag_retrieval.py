from app.services.embedding_service import embed_chunks, embed_text
from app.services.vector_store import VectorStore


print("Real embedding + FAISS retrieval test")
print("-" * 60)


# --------------------------------------------------
# Create realistic transcript chunks
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
# Generate real Gemini embeddings
# --------------------------------------------------

print("Generating embeddings...")

embedded_chunks = embed_chunks(chunks)

print(
    "Embedded chunks:",
    len(embedded_chunks)
)

print(
    "Embedding dimensions:",
    len(embedded_chunks[0]["embedding"])
)


# --------------------------------------------------
# Create FAISS vector store
# --------------------------------------------------

dimension = len(
    embedded_chunks[0]["embedding"]
)

store = VectorStore(
    dimension=dimension
)


store.add_chunks(
    embedded_chunks
)


print("\nVectors stored in FAISS:", store.index.ntotal)


# --------------------------------------------------
# Create a real question
# --------------------------------------------------

question = (
    "How does supervised learning work?"
)


print("\nQuestion:")
print(question)


# --------------------------------------------------
# Embed the question
# --------------------------------------------------

print("\nGenerating question embedding...")

question_embedding = embed_text(
    question
)


print(
    "Question embedding dimensions:",
    len(question_embedding)
)


# --------------------------------------------------
# Search FAISS
# --------------------------------------------------

results = store.search(
    question_embedding,
    top_k=2
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\nRetrieved chunks")
print("-" * 60)


for index, result in enumerate(
    results,
    start=1
):

    print(f"\nResult {index}")

    print(
        "Start:",
        result["start"]
    )

    print(
        "End:",
        result["end"]
    )

    print(
        "Distance:",
        result["distance"]
    )

    print(
        "Text:",
        result["text"]
    )


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert len(results) == 2

assert (
    results[0]["text"]
    == chunks[1]["text"]
)

assert results[0]["start"] == 8.0
assert results[0]["end"] == 16.0


print("\n" + "-" * 60)
print("Real RAG retrieval test passed successfully!")