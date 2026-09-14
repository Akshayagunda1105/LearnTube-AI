from youtube_transcript_api import YouTubeTranscriptApi


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

    return {
        "language": fetched.language,
        "language_code": fetched.language_code,
        "is_generated": fetched.is_generated,
        "segments": [
            {
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration,
            }
            for snippet in fetched
        ],
    }