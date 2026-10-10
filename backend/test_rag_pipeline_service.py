
import pytest
from unittest.mock import patch

from app.services.rag_pipeline_service import (
    build_video_rag,
    rag_cache,
)


VIDEO_ID = "test-rag-pipeline-video"


@pytest.fixture(autouse=True)
def clear_test_cache():
    rag_cache.pop(VIDEO_ID, None)
    yield
    rag_cache.pop(VIDEO_ID, None)


@patch("app.services.rag_pipeline_service.fetch_transcript")
def test_build_video_rag_propagates_transcript_failure(
    mock_fetch_transcript,
):
    mock_fetch_transcript.side_effect = RuntimeError(
        "Simulated transcript fetch failure"
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated transcript fetch failure",
    ):
        build_video_rag(VIDEO_ID)

    mock_fetch_transcript.assert_called_once_with(VIDEO_ID)
    assert VIDEO_ID not in rag_cache


@pytest.mark.parametrize(
    "transcript_data",
    [
        {},
        {
            "english_segments": [],
        },
        {
            "english_segments": [],
            "language": "English",
            "language_code": "en",
            "is_generated": False,
            "original_segments": [],
        },
    ],
)
@patch("app.services.rag_pipeline_service.fetch_transcript")
def test_build_video_rag_rejects_empty_transcript(
    mock_fetch_transcript,
    transcript_data,
):
    mock_fetch_transcript.return_value = transcript_data

    with pytest.raises(
        ValueError,
        match="Transcript data is empty|English transcript contains no segments",
    ):
        build_video_rag(VIDEO_ID)

    assert VIDEO_ID not in rag_cache


@patch("app.services.rag_pipeline_service.embed_chunks")
@patch("app.services.rag_pipeline_service.create_rag_chunks")
@patch("app.services.rag_pipeline_service.fetch_transcript")
def test_build_video_rag_rejects_empty_chunks(
    mock_fetch_transcript,
    mock_create_chunks,
    mock_embed_chunks,
):
    mock_fetch_transcript.return_value = {
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "original_segments": [
            {"text": "Example", "start": 0.0, "duration": 2.0}
        ],
        "english_segments": [
            {"text": "Example", "start": 0.0, "duration": 2.0}
        ],
    }
    mock_create_chunks.return_value = []

    with pytest.raises(
        ValueError,
        match="No RAG chunks were created",
    ):
        build_video_rag(VIDEO_ID)

    mock_embed_chunks.assert_not_called()
    assert VIDEO_ID not in rag_cache


@patch("app.services.rag_pipeline_service.embed_chunks")
@patch("app.services.rag_pipeline_service.create_rag_chunks")
@patch("app.services.rag_pipeline_service.fetch_transcript")
def test_build_video_rag_propagates_embedding_failure(
    mock_fetch_transcript,
    mock_create_chunks,
    mock_embed_chunks,
):
    mock_fetch_transcript.return_value = {
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "original_segments": [],
        "english_segments": [
            {"text": "Example", "start": 0.0, "duration": 2.0}
        ],
    }
    mock_create_chunks.return_value = [
        {"text": "Example", "start": 0.0, "end": 2.0}
    ]
    mock_embed_chunks.side_effect = RuntimeError(
        "Simulated embedding failure"
    )

    with pytest.raises(RuntimeError, match="Simulated embedding failure"):
        build_video_rag(VIDEO_ID)

    assert VIDEO_ID not in rag_cache


@patch("app.services.rag_pipeline_service.embed_chunks")
@patch("app.services.rag_pipeline_service.create_rag_chunks")
@patch("app.services.rag_pipeline_service.fetch_transcript")
def test_build_video_rag_rejects_empty_embedding_results(
    mock_fetch_transcript,
    mock_create_chunks,
    mock_embed_chunks,
):
    mock_fetch_transcript.return_value = {
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "original_segments": [],
        "english_segments": [
            {"text": "Example", "start": 0.0, "duration": 2.0}
        ],
    }
    mock_create_chunks.return_value = [
        {"text": "Example", "start": 0.0, "end": 2.0}
    ]
    mock_embed_chunks.return_value = []

    with pytest.raises(
        ValueError,
        match="Embedding generation returned no chunks",
    ):
        build_video_rag(VIDEO_ID)

    assert VIDEO_ID not in rag_cache


@patch("app.services.rag_pipeline_service.VectorStore")
@patch("app.services.rag_pipeline_service.embed_chunks")
@patch("app.services.rag_pipeline_service.create_rag_chunks")
@patch("app.services.rag_pipeline_service.fetch_transcript")
def test_build_video_rag_propagates_vector_store_failure(
    mock_fetch_transcript,
    mock_create_chunks,
    mock_embed_chunks,
    mock_vector_store_class,
):
    mock_fetch_transcript.return_value = {
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "original_segments": [],
        "english_segments": [
            {"text": "Example", "start": 0.0, "duration": 2.0}
        ],
    }
    mock_create_chunks.return_value = [
        {"text": "Example", "start": 0.0, "end": 2.0}
    ]
    mock_embed_chunks.return_value = [
        {
            "text": "Example",
            "start": 0.0,
            "end": 2.0,
            "embedding": [0.1, 0.2],
        }
    ]
    mock_vector_store_class.return_value.add_chunks.side_effect = RuntimeError(
        "Simulated vector store failure"
    )

    with pytest.raises(RuntimeError, match="Simulated vector store failure"):
        build_video_rag(VIDEO_ID)

    assert VIDEO_ID not in rag_cache
