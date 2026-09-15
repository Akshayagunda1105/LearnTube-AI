from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()


def create_summary_chunks(segments, max_chars=6000):
    """
    Split transcript segments into chunks for summarization.

    Each chunk keeps the original transcript text and timestamps.
    A segment is never split between chunks.
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

        # If adding this segment exceeds the limit,
        # start a new chunk.
        if current_chunk and current_chars + segment_chars > max_chars:
            chunks.append(current_chunk)
            current_chunk = []
            current_chars = 0

        current_chunk.append(segment_with_id)
        current_chars += segment_chars

    # Add the final chunk.
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def summarize_chunk(chunk):
    """
    Generate a concise summary for one transcript chunk.

    The summary should contain only information present
    in the transcript.
    """

    transcript_text = "\n".join(
        segment["text"]
        for segment in chunk
    )

    prompt = f"""
You are summarizing a transcript from an educational YouTube video.

Create a concise and informative summary of the transcript below.

Rules:
- Use only information present in the transcript.
- Do not invent facts or add outside information.
- Focus on the main ideas and important concepts.
- Remove repetition and unnecessary conversational words.
- Preserve important technical terms.
- Write the summary in clear English.
- Return only the summary.
- Do not use headings.
- Do not mention that you are summarizing a transcript.

Transcript:
{transcript_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()