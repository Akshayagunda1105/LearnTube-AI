from app.services.embedding_service import (
    embed_text,
    embed_chunks,
)


print("Embedding service test")
print("-" * 60)


# --------------------------------------------------
# Test 1: Single text embedding
# --------------------------------------------------

text = (
    "Machine learning allows computers to learn "
    "patterns from data."
)

print("\nTesting embed_text()...")

embedding = embed_text(text)

print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])


assert isinstance(embedding, list)
assert len(embedding) > 0


# --------------------------------------------------
# Test 2: Multiple RAG chunk embeddings
# --------------------------------------------------

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


print("\nTesting embed_chunks()...")

embedded_chunks = embed_chunks(chunks)

print("Total embedded chunks:", len(embedded_chunks))


assert len(embedded_chunks) == len(chunks)


for index, chunk in enumerate(embedded_chunks):

    print(f"\nChunk {index + 1}")
    print("Start:", chunk["start"])
    print("End:", chunk["end"])
    print("Vector dimensions:", len(chunk["embedding"]))

    assert chunk["text"] == chunks[index]["text"]
    assert chunk["start"] == chunks[index]["start"]
    assert chunk["end"] == chunks[index]["end"]

    assert isinstance(chunk["embedding"], list)
    assert len(chunk["embedding"]) > 0


print("\n" + "-" * 60)
print("Embedding service test passed successfully!")