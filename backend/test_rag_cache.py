from app.services.rag_pipeline_service import rag_cache


VIDEO_ID = "test_video_123"


fake_rag_data = {
    "video_id": VIDEO_ID,
    "vector_store": "fake_vector_store"
}


print("Adding RAG data to cache...")

rag_cache[VIDEO_ID] = fake_rag_data


print("Checking whether video is cached...")

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