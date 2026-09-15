from dotenv import load_dotenv
from google import genai
import json


load_dotenv()

client = genai.Client()


def create_batches(segments, max_chars=6000):
    """
    Split transcript segments into batches based on character count.

    Each segment remains intact and keeps its original position.
    """

    batches = []
    current_batch = []
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
        # start a new batch.
        if current_batch and current_chars + segment_chars > max_chars:
            batches.append(current_batch)
            current_batch = []
            current_chars = 0

        current_batch.append(segment_with_id)
        current_chars += segment_chars

    # Add the final batch.
    if current_batch:
        batches.append(current_batch)

    return batches


def translate_text(text: str, source_language: str) -> str:
    """
    Translate text from the source language to English.
    """

    prompt = f"""
Translate the following text from {source_language} to English.

Rules:
- Return only the English translation.
- Do not explain the translation.
- Do not add extra information.
- Preserve the original meaning.
- Keep technical terms accurate.

Text:
{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()


def translate_batch(batch, source_language: str):
    """
    Translate a batch of transcript segments into English.

    Uses Gemini structured JSON output and validates
    the returned segment IDs.
    """

    segments_text = "\n".join(
        f"[{segment['id']}] {segment['text']}"
        for segment in batch
    )

    prompt = f"""
Translate the following transcript segments from {source_language} to English.

Rules:
- Keep the same ID for every segment.
- Do not add, remove, merge, or split segments.
- Translate each segment independently.
- Return exactly one translation for every input segment.
- Do not include timestamps.
- Preserve the original meaning.
- Do not add explanations.

Input segments:
{segments_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {
                            "type": "INTEGER"
                        },
                        "translation": {
                            "type": "STRING"
                        }
                    },
                    "required": [
                        "id",
                        "translation"
                    ]
                }
            }
        }
    )

    raw_response = response.text.strip()

    try:
        translations = json.loads(raw_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemini returned invalid JSON: {error}"
        )

    if not isinstance(translations, list):
        raise ValueError(
            "Gemini response must be a JSON array"
        )

    expected_ids = {
        segment["id"]
        for segment in batch
    }

    received_ids = set()

    validated_translations = []

    for item in translations:

        if not isinstance(item, dict):
            raise ValueError(
                "Each translation must be an object"
            )

        if "id" not in item or "translation" not in item:
            raise ValueError(
                "Each translation must contain id and translation"
            )

        try:
            raw_id = str(item["id"]).strip()

            # Handle IDs such as "[0]" if Gemini ever returns them.
            if raw_id.startswith("[") and raw_id.endswith("]"):
                raw_id = raw_id[1:-1].strip()

            segment_id = int(raw_id)

        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid segment ID: {item['id']}"
            )

        if segment_id in received_ids:
            raise ValueError(
                f"Duplicate segment ID: {segment_id}"
            )

        received_ids.add(segment_id)

        translation = str(
            item["translation"]
        ).strip()

        if not translation:
            raise ValueError(
                f"Empty translation for segment {segment_id}"
            )

        validated_translations.append(
            {
                "id": segment_id,
                "translation": translation,
            }
        )

    if received_ids != expected_ids:
        raise ValueError(
            f"Segment ID mismatch. "
            f"Expected: {expected_ids}, "
            f"Received: {received_ids}"
        )

    # Return translations in the same order as the input batch.
    validated_translations.sort(
        key=lambda item: item["id"]
    )

    return validated_translations