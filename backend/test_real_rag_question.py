from app.services.rag_pipeline_service import build_video_rag
from app.services.rag_service import answer_question


VIDEO_ID = "i_LwzRVP7bg"

QUESTION = "What is supervised learning?"


# Build RAG from the real YouTube video
result = build_video_rag(VIDEO_ID)

vector_store = result["vector_store"]


# Ask a question
response = answer_question(
    QUESTION,
    vector_store,
    top_k=3
)


print("\nQuestion:")
print(QUESTION)

print("\nAnswer:")
print(response["answer"])

print("\nSources:")

for index, source in enumerate(response["sources"], start=1):
    print(f"\nSource {index}")
    print("Start:", source["start"])
    print("End:", source["end"])
    print("Distance:", source["distance"])
    print("Text:", source["text"])