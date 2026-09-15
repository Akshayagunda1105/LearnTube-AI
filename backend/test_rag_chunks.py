from app.services.rag_service import create_rag_chunks


test_segments = [
    {
        "text": "Machine learning allows computers to learn patterns from data.",
        "start": 0.0,
        "duration": 5.0,
    },
    {
        "text": "Supervised learning uses labeled examples to train models.",
        "start": 5.0,
        "duration": 5.0,
    },
    {
        "text": "The model learns from these examples and makes predictions.",
        "start": 10.0,
        "duration": 5.0,
    },
    {
        "text": "Unsupervised learning works with unlabeled data.",
        "start": 15.0,
        "duration": 5.0,
    },
]


print("RAG chunking test")
print("-" * 60)


chunks = create_rag_chunks(
    test_segments,
    max_chars=130
)


print("Total chunks:", len(chunks))


for index, chunk in enumerate(chunks, start=1):

    print(f"\nChunk {index}")
    print("-" * 60)

    print("Start:", chunk["start"])
    print("End:", chunk["end"])
    print("Text:", chunk["text"])


# Basic validation.
assert isinstance(chunks, list)
assert len(chunks) > 0


# Verify every chunk has the required fields.
for chunk in chunks:

    assert "text" in chunk
    assert "start" in chunk
    assert "end" in chunk

    assert isinstance(chunk["text"], str)
    assert len(chunk["text"].strip()) > 0


# Verify timestamps are valid.
for chunk in chunks:

    assert chunk["start"] < chunk["end"]


print("\n" + "-" * 60)
print("RAG chunking test passed successfully!")