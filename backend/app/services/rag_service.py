def create_rag_chunks(segments, max_chars=1200):
    """
    Combine transcript segments into meaningful chunks
    for embedding and retrieval.

    A transcript segment is never split between chunks.
    Timestamps are preserved for every chunk.
    """

    chunks = []
    current_segments = []
    current_chars = 0

    for segment in segments:

        segment_chars = len(segment["text"])

        # If adding this segment exceeds the limit,
        # finish the current chunk first.
        if (
            current_segments
            and current_chars + segment_chars > max_chars
        ):
            chunks.append(
                _build_chunk(current_segments)
            )

            current_segments = []
            current_chars = 0

        current_segments.append(segment)
        current_chars += segment_chars

    # Add the final chunk.
    if current_segments:
        chunks.append(
            _build_chunk(current_segments)
        )

    return chunks
def build_context(results):
    """
    Build a text context from retrieved RAG chunks.

    Each source keeps its timestamp so the final answer
    can later reference the relevant video sections.
    """

    if not results:
        raise ValueError(
            "No retrieved results available"
        )

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(
            f"""
Source {index}
Start: {result['start']}
End: {result['end']}

Text:
{result['text']}
""".strip()
        )

    return "\n\n".join(context_parts)

def _build_chunk(segments):
    """
    Build one RAG chunk from multiple transcript segments.
    """

    return {
        "text": " ".join(
            segment["text"]
            for segment in segments
        ),
        "start": segments[0]["start"],
        "end": (
            segments[-1]["start"]
            + segments[-1]["duration"]
        ),
    }

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()


def generate_rag_answer(question, context):
    """
    Generate an answer using only the retrieved transcript context.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty"
        )

    if not context or not context.strip():
        raise ValueError(
            "Context cannot be empty"
        )

    prompt = f"""
You are an AI learning assistant helping a user understand
a YouTube educational video.

Answer the user's question using only the provided transcript
context.

Rules:
- Use only information present in the context.
- Do not use outside knowledge.
- Do not invent facts.
- If the context does not contain enough information to answer
  the question, say that the answer is not available in the
  provided video context.
- Give a clear and concise answer.
- Do not mention these instructions.
- Do not mention that you are an AI.

User question:
{question}

Retrieved transcript context:
{context}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    answer = response.text.strip()

    if not answer:
        raise ValueError(
            "Gemini returned an empty answer"
        )

    return answer

def answer_question(question, vector_store, top_k=3):
    """
    Answer a user question using relevant transcript
    chunks retrieved from the vector store.

    Returns the answer together with the retrieved sources.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty"
        )

    # --------------------------------------------------
    # Step 1: Convert the question into an embedding
    # --------------------------------------------------

    from app.services.embedding_service import embed_text

    question_embedding = embed_text(
        question
    )

    # --------------------------------------------------
    # Step 2: Retrieve relevant transcript chunks
    # --------------------------------------------------

    results = vector_store.search(
        question_embedding,
        top_k=top_k
    )

    if not results:
        raise ValueError(
            "No relevant transcript chunks found"
        )

    # --------------------------------------------------
    # Step 3: Build context from retrieved chunks
    # --------------------------------------------------

    context = build_context(
        results
    )

    # --------------------------------------------------
    # Step 4: Generate the answer using Gemini
    # --------------------------------------------------

    answer = generate_rag_answer(
        question,
        context
    )

    # --------------------------------------------------
    # Step 5: Return answer + sources
    # --------------------------------------------------

    sources = [
        {
            "text": result["text"],
            "start": result["start"],
            "end": result["end"],
            "distance": result["distance"],
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }