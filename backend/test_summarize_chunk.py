from app.services.summarizer_service import (
    create_summary_chunks,
    summarize_chunk,
)


test_segments = [
    {
        "text": "Machine learning is a field of artificial intelligence that allows computers to learn patterns from data.",
        "start": 0.0,
        "duration": 5.0,
    },
    {
        "text": "Supervised learning uses labeled examples to train a model to make predictions.",
        "start": 5.0,
        "duration": 5.0,
    },
    {
        "text": "For example, a model can learn from labeled images to recognize whether an image contains a cat or a dog.",
        "start": 10.0,
        "duration": 6.0,
    },
]


print("Gemini chunk summarization test")
print("-" * 60)


chunks = create_summary_chunks(
    test_segments,
    max_chars=1000
)

print("Total chunks:", len(chunks))


chunk = chunks[0]

print("\nTranscript chunk")
print("-" * 60)

for segment in chunk:
    print(
        f"[{segment['start']}s] "
        f"{segment['text']}"
    )


print("\nGenerating summary...")
print("-" * 60)

result = summarize_chunk(chunk)

print("Start timestamp:", result["start"])
print("End timestamp:", result["end"])
print("Summary:")
print(result["summary"])

assert isinstance(result, dict)

assert "start" in result
assert "end" in result
assert "summary" in result

assert result["start"] == chunk[0]["start"]

expected_end = (
    chunk[-1]["start"]
    + chunk[-1]["duration"]
)

assert result["end"] == expected_end

assert isinstance(result["summary"], str)
assert len(result["summary"].strip()) > 0

print("\n" + "-" * 60)
print("Gemini chunk summarization test passed successfully!")