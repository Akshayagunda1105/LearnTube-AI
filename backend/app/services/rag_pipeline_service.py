
import logging
import time

from app.services.transcript_service import fetch_transcript
from app.services.rag_service import create_rag_chunks
from app.services.embedding_service import embed_chunks
from app.services.vector_store import VectorStore


logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 3072


# Temporary in-memory cache for RAG vector stores.
# Key: video_id
# Value: RAG data for that video
rag_cache = {}


def build_video_rag(video_id: str):
    """
    Build a FAISS vector store from a YouTube video's
    English transcript, with diagnostics for each stage.
    """

    # Stage 1: Fetch the transcript.
    start_time = time.perf_counter()

    try:
        transcript_data = fetch_transcript(video_id)
    except Exception:
        logger.exception(
            "RAG stage=transcript_fetch status=failed video_id=%s",
            video_id,
        )
        raise

    if not transcript_data:
        logger.error(
            "RAG stage=transcript_fetch status=empty video_id=%s",
            video_id,
        )
        raise ValueError("Transcript data is empty")

    logger.info(
        "RAG stage=transcript_fetch status=success "
        "video_id=%s duration_ms=%.2f",
        video_id,
        (time.perf_counter() - start_time) * 1000,
    )

    # Stage 2: Validate English transcript segments.
    english_segments = transcript_data.get("english_segments", [])

    if not english_segments:
        logger.error(
            "RAG stage=transcript_validation status=empty "
            "video_id=%s",
            video_id,
        )
        raise ValueError("English transcript contains no segments")

    logger.info(
        "RAG stage=transcript_validation status=success "
        "video_id=%s segment_count=%d",
        video_id,
        len(english_segments),
    )

    # Stage 3: Create RAG chunks.
    start_time = time.perf_counter()

    try:
        rag_chunks = create_rag_chunks(english_segments)
    except Exception:
        logger.exception(
            "RAG stage=chunking status=failed video_id=%s",
            video_id,
        )
        raise

    if not rag_chunks:
        logger.error(
            "RAG stage=chunking status=empty video_id=%s",
            video_id,
        )
        raise ValueError("No RAG chunks were created")

    logger.info(
        "RAG stage=chunking status=success "
        "video_id=%s chunk_count=%d duration_ms=%.2f",
        video_id,
        len(rag_chunks),
        (time.perf_counter() - start_time) * 1000,
    )

    # Stage 4: Generate embeddings.
    start_time = time.perf_counter()

    try:
        embedded_chunks = embed_chunks(rag_chunks)
    except Exception:
        logger.exception(
            "RAG stage=embedding status=failed "
            "video_id=%s chunk_count=%d",
            video_id,
            len(rag_chunks),
        )
        raise

    if not embedded_chunks:
        logger.error(
            "RAG stage=embedding status=empty video_id=%s",
            video_id,
        )
        raise ValueError("Embedding generation returned no chunks")

    logger.info(
        "RAG stage=embedding status=success "
        "video_id=%s embedded_count=%d duration_ms=%.2f",
        video_id,
        len(embedded_chunks),
        (time.perf_counter() - start_time) * 1000,
    )

    # Stage 5: Create and populate the FAISS vector store.
    try:
        vector_store = VectorStore(
            dimension=EMBEDDING_DIMENSION
        )

        vector_store.add_chunks(embedded_chunks)
    except Exception:
        logger.exception(
            "RAG stage=vector_store status=failed video_id=%s",
            video_id,
        )
        raise

    logger.info(
        "RAG stage=vector_store status=success "
        "video_id=%s vector_count=%d",
        video_id,
        vector_store.index.ntotal,
    )

    # Stage 6: Prepare and cache the completed RAG data.
    rag_data = {
        "video_id": video_id,
        "language": transcript_data["language"],
        "language_code": transcript_data["language_code"],
        "is_generated": transcript_data["is_generated"],
        "original_segments": transcript_data["original_segments"],
        "english_segments": english_segments,
        "rag_chunks": rag_chunks,
        "vector_store": vector_store,
    }

    rag_cache[video_id] = rag_data

    logger.info(
        "RAG stage=cache status=stored video_id=%s",
        video_id,
    )

    return rag_data


def get_video_rag(video_id: str):
    """
    Return cached RAG data when available.
    Otherwise, build and cache it.
    """

    if video_id in rag_cache:
        logger.info(
            "RAG stage=cache status=hit video_id=%s",
            video_id,
        )
        return rag_cache[video_id]

    logger.info(
        "RAG stage=cache status=miss video_id=%s",
        video_id,
    )

    return build_video_rag(video_id)


def get_cached_video_rag(video_id: str):
    """
    Return cached RAG data without building a new index.
    """

    return rag_cache.get(video_id)
