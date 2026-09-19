def create_note_chunks(segments, max_chars=6000):
    """
    Split transcript segments into chunks for note generation.

    Each chunk preserves:
    - transcript text
    - timestamp
    - duration
    - original segment ID

    A transcript segment is never split between chunks.
    """

    chunks = []

    current_chunk = []
    current_chars = 0

    for index, segment in enumerate(segments):

        segment_with_id = {
            "id": index,
            "text": segment["text"],
            "start": segment["start"],
            "duration": segment["duration"],
        }

        segment_chars = len(segment["text"])

        # If adding this segment would exceed
        # the character limit, start a new chunk.
        if (
            current_chunk
            and current_chars + segment_chars > max_chars
        ):
            chunks.append(current_chunk)

            current_chunk = []
            current_chars = 0

        current_chunk.append(segment_with_id)
        current_chars += segment_chars

    # Add the final chunk.
    if current_chunk:
        chunks.append(current_chunk)

    return chunks