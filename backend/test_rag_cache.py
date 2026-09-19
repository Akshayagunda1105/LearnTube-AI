from app.services.rag_pipeline_service import rag_cache


VIDEO_ID = "test_video_123"


fake_rag_data = {
    "video_id": VIDEO_ID,

    "language": "Telugu",
    "language_code": "te",
    "is_generated": True,

    "original_segments": [
        {
            "text": "నమస్కారం",
            "start": 0.0,
            "duration": 2.0,
        }
    ],

    "english_segments": [
        {
            "text": "Hello",
            "start": 0.0,
            "duration": 2.0,
        }
    ],

    "rag_chunks": [
        {
            "text": "Hello",
            "start": 0.0,
            "end": 2.0,
        }
    ],

    "vector_store": "fake_vector_store",
}


print("Adding RAG data to cache...")
rag_cache[VIDEO_ID] = fake_rag_data


print("\nChecking whether video is cached...")

if VIDEO_ID in rag_cache:
    print("Video found in cache.")
else:
    print("Video not found in cache.")


print("\nChecking whether the cached object is reused...")

first_result = rag_cache[VIDEO_ID]
second_result = rag_cache[VIDEO_ID]

print(
    first_result is second_result
)


print("\nChecking cached transcript data...")

assert first_result["original_segments"] == fake_rag_data["original_segments"]
assert first_result["english_segments"] == fake_rag_data["english_segments"]

print("Original transcript found in cache.")
print("English transcript found in cache.")


print("\nChecking cached language information...")

assert first_result["language"] == "Telugu"
assert first_result["language_code"] == "te"
assert first_result["is_generated"] is True

print("Language information found in cache.")


print("\nRAG cache test passed successfully!")