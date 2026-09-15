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