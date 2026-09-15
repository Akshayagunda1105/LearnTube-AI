from app.services.summarizer_service import (
    combine_chunk_summaries,
    generate_final_summary,
)


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


print("Final summary generation test")
print("-" * 60)


combined = combine_chunk_summaries(
    chunk_summaries
)


print("Generating final summary...")
print("-" * 60)


final_summary = generate_final_summary(
    combined
)


print("\nFinal Summary")
print("-" * 60)
print(final_summary)


assert isinstance(final_summary, str)
assert len(final_summary.strip()) > 0


print("\n" + "-" * 60)
print("Final summary generation test passed successfully!")