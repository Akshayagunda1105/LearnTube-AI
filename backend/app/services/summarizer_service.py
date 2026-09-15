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

    Returns the summary together with the chunk's
    start and end timestamps.
    """

    transcript_text = "\n".join(
        segment["text"]
        for segment in chunk
    )

    start_time = chunk[0]["start"]

    end_time = (
        chunk[-1]["start"]
        + chunk[-1]["duration"]
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

    summary = response.text.strip()

    if not summary:
        raise ValueError(
            "Gemini returned an empty summary"
        )

    return {
        "start": start_time,
        "end": end_time,
        "summary": summary,
    }


def combine_chunk_summaries(chunk_summaries):
    """
    Combine multiple chunk summaries into one text input
    for the final summarization step.

    Each chunk summary keeps its timestamp information.
    """

    summaries = []

    for index, chunk in enumerate(chunk_summaries, start=1):

        summaries.append(
            f"""
Chunk {index}
Start: {chunk['start']}
End: {chunk['end']}

Summary:
{chunk['summary']}
""".strip()
        )

    return "\n\n".join(summaries)

def generate_final_summary(combined_summaries):
    """
    Generate one final summary from multiple chunk summaries.

    Gemini receives the summaries produced from each transcript
    chunk and combines them into one coherent summary.
    """

    prompt = f"""
You are creating the final summary of an educational YouTube video.

Below are summaries of different sections of the video.

Create one coherent and informative summary of the entire video.

Rules:
- Use only information present in the provided summaries.
- Do not invent facts or add outside information.
- Combine related ideas instead of repeating them.
- Focus on the most important concepts.
- Preserve important technical terms.
- Write in clear and concise English.
- Organize the ideas in a logical order.
- Return only the final summary.
- Do not mention the chunk summaries.
- Do not mention that you are an AI.

Section summaries:

{combined_summaries}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    final_summary = response.text.strip()

    if not final_summary:
        raise ValueError(
            "Gemini returned an empty final summary"
        )

    return final_summary