from app.services.rag_pipeline_service import build_video_rag


VIDEO_ID = "i_LwzRVP7bg"


result = build_video_rag(VIDEO_ID)

print("Video ID:", result["video_id"])
print("Language:", result["language"])
print("Language Code:", result["language_code"])
print("Generated:", result["is_generated"])
print("Number of RAG chunks:", len(result["rag_chunks"]))
print("FAISS vectors:", result["vector_store"].index.ntotal)