from app.services.summarizer_service import combine_chunk_summaries


chunk_summaries = [
    {
        "start": 0.0,
        "end": 60.0,
        "summary": (
            "Machine learning allows computers to learn "
            "patterns from data."
        ),
    },
    {
        "start": 60.0,
        "end": 120.0,
        "summary": (
            "Supervised learning uses labeled examples "
            "to train predictive models."
        ),
    },
    {
        "start": 120.0,
        "end": 180.0,
        "summary": (
            "Unsupervised learning discovers patterns "
            "in unlabeled data."
        ),
    },
]


print("Chunk summary combination test")
print("-" * 60)

print("Total chunk summaries:", len(chunk_summaries))


combined = combine_chunk_summaries(
    chunk_summaries
)


print("\nCombined summaries")
print("-" * 60)

print(combined)


# Basic validation.
assert isinstance(combined, str)
assert len(combined.strip()) > 0


# Verify that every chunk summary is present.
for chunk in chunk_summaries:

    assert chunk["summary"] in combined
    assert str(chunk["start"]) in combined
    assert str(chunk["end"]) in combined


print("\n" + "-" * 60)
print("Chunk summary combination test passed successfully!")