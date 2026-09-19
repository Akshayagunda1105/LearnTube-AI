import json

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
    Generate a structured final summary from multiple
    transcript chunk summaries.

    Returns:
        dict containing:
        - overview
        - key_points
        - concepts
        - takeaways
    """

    prompt = f"""
You are creating the final study summary of an educational
YouTube video.

Below are summaries of different sections of the video.

Create one coherent and useful study summary containing:

1. overview
   - A concise explanation of what the entire video teaches.

2. key_points
   - The most important points from the video.
   - Return these as a list of concise strings.

3. concepts
   - Identify the important concepts taught in the video.
   - For each concept, provide:
     - title
     - explanation

4. takeaways
   - The most important things a learner should remember.

Rules:
- Use only information present in the provided summaries.
- Do not invent facts or add outside information.
- Combine related ideas instead of repeating them.
- Preserve important technical terms.
- Write in clear and concise English.
- Make the result useful for a student revising the video.
- Return ONLY valid JSON.
- Do not wrap the JSON in Markdown code fences.

Return exactly this structure:

{{
  "overview": "string",
  "key_points": [
    "string"
  ],
  "concepts": [
    {{
      "title": "string",
      "explanation": "string"
    }}
  ],
  "takeaways": [
    "string"
  ]
}}

Section summaries:

{combined_summaries}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty final summary"
        )

    response_text = response.text.strip()

    # Handle the occasional Markdown code fence
    # even though the prompt asks for plain JSON.
    if response_text.startswith("```json"):
        response_text = response_text[7:]

    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        final_summary = json.loads(response_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned invalid JSON"
        ) from error

    required_fields = [
        "overview",
        "key_points",
        "concepts",
        "takeaways",
    ]

    for field in required_fields:
        if field not in final_summary:
            raise ValueError(
                f"Summary is missing required field: {field}"
            )

    if not isinstance(final_summary["overview"], str):
        raise ValueError(
            "Summary overview must be a string"
        )

    if not isinstance(final_summary["key_points"], list):
        raise ValueError(
            "Summary key_points must be a list"
        )

    if not isinstance(final_summary["concepts"], list):
        raise ValueError(
            "Summary concepts must be a list"
        )

    if not isinstance(final_summary["takeaways"], list):
        raise ValueError(
            "Summary takeaways must be a list"
        )

    return final_summary