
import os

import pytest

from app.services.rag_pipeline_service import build_video_rag


VIDEO_ID = "i_LwzRVP7bg"


@pytest.mark.skipif(
    os.getenv("RUN_REAL_RAG_TEST") != "1",
    reason="Real RAG integration test is opt-in because it uses external APIs.",
)
def test_real_rag_pipeline():
    result = build_video_rag(VIDEO_ID)

    assert result["video_id"] == VIDEO_ID
    assert result["rag_chunks"]
    assert result["vector_store"].index.ntotal > 0
