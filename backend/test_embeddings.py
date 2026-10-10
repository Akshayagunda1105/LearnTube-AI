
import os

import pytest
from dotenv import load_dotenv
from google import genai


load_dotenv()


@pytest.mark.skipif(
    os.getenv("RUN_REAL_RAG_TEST") != "1",
    reason="Live Gemini API test is opt-in.",
)
def test_gemini_embedding():
    client = genai.Client()

    text = """
    Machine learning allows computers to learn patterns
    from data and make predictions.
    """

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    embedding = response.embeddings[0].values

    assert isinstance(embedding, list)
    assert len(embedding) > 0
