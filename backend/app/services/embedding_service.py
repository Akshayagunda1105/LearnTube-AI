from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()


EMBEDDING_MODEL = "gemini-embedding-001"


def embed_text(text: str):
    """
    Convert a single piece of text into an embedding vector.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    embedding = response.embeddings[0].values

    if not embedding:
        raise ValueError(
            "Gemini returned an empty embedding"
        )

    return embedding


def embed_chunks(chunks):
    """
    Generate embeddings for multiple RAG chunks.

    Returns the original chunk information together
    with its embedding vector.
    """

    if not chunks:
        raise ValueError("Chunks cannot be empty")

    embedded_chunks = []

    for chunk in chunks:

        if not chunk.get("text", "").strip():
            raise ValueError(
                "RAG chunk text cannot be empty"
            )

        embedding = embed_text(
            chunk["text"]
        )

        embedded_chunks.append(
            {
                "text": chunk["text"],
                "start": chunk["start"],
                "end": chunk["end"],
                "embedding": embedding,
            }
        )

    return embedded_chunks