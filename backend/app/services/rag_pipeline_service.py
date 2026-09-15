from app.services.transcript_service import fetch_transcript
from app.services.rag_service import create_rag_chunks
from app.services.embedding_service import embed_chunks
from app.services.vector_store import VectorStore


EMBEDDING_DIMENSION = 3072


def build_video_rag(video_id: str):
    """
    Build a FAISS vector store from a YouTube video's
    English transcript.
    """

    # 1. Fetch the transcript
    transcript_data = fetch_transcript(video_id)

    # 2. Use the English transcript for RAG
    english_segments = transcript_data["english_segments"]

    # 3. Convert transcript segments into RAG chunks
    rag_chunks = create_rag_chunks(english_segments)

    # 4. Generate embeddings for each chunk
    embedded_chunks = embed_chunks(rag_chunks)

    # 5. Create the FAISS vector store
    vector_store = VectorStore(
        dimension=EMBEDDING_DIMENSION
    )

    # 6. Add the embedded chunks
    vector_store.add_chunks(embedded_chunks)

    return {
        "video_id": video_id,
        "language": transcript_data["language"],
        "language_code": transcript_data["language_code"],
        "is_generated": transcript_data["is_generated"],
        "rag_chunks": rag_chunks,
        "vector_store": vector_store,
    }