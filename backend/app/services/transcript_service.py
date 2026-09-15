from youtube_transcript_api import YouTubeTranscriptApi
from app.services.translation_service import create_batches, translate_batch


def fetch_transcript(video_id: str):
    """
    Fetch the best available transcript for a YouTube video.

    Preference:
    1. Manually created transcript
    2. Auto-generated transcript
    """

    api = YouTubeTranscriptApi()

    transcript_list = api.list(video_id)

    # Prefer a manually created transcript.
    try:
        transcript = next(
            transcript
            for transcript in transcript_list
            if not transcript.is_generated
        )
    except StopIteration:
        # Fall back to an auto-generated transcript.
        try:
            transcript = next(
                transcript
                for transcript in transcript_list
                if transcript.is_generated
            )
        except StopIteration:
            raise ValueError("No transcript available for this video")

    fetched = transcript.fetch()

    original_segments = [
        {
            "text": snippet.text,
            "start": snippet.start,
            "duration": snippet.duration,
        }
        for snippet in fetched
    ]

    # English transcripts don't need translation.
    if fetched.language_code == "en":
        english_segments = original_segments

    else:
        # Split the transcript into manageable batches.
        batches = create_batches(
            original_segments,
            max_chars=3000
        )

        translated_segments = []

        # Translate each batch using Gemini.
        for batch in batches:
            translations = translate_batch(
                batch,
                fetched.language
            )

            translated_segments.extend(translations)

        # Create a mapping from segment ID to translated text.
        translations_by_id = {
            item["id"]: item["translation"]
            for item in translated_segments
        }

        english_segments = []

        # Reconstruct the translated transcript while
        # preserving the original timestamps.
        for index, segment in enumerate(original_segments):

            if index not in translations_by_id:
                raise ValueError(
                    f"Missing translation for segment {index}"
                )

            english_segments.append(
                {
                    "text": translations_by_id[index],
                    "start": segment["start"],
                    "duration": segment["duration"],
                }
            )

    return {
        "language": fetched.language,
        "language_code": fetched.language_code,
        "is_generated": fetched.is_generated,
        "original_segments": original_segments,
        "english_segments": english_segments,
    }