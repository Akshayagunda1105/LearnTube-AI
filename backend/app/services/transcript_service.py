from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str):
    """
    Fetch the best available English transcript for a YouTube video.
    """

    api = YouTubeTranscriptApi()

    transcript_list = api.list(video_id)

    # Prefer manually created English captions.
    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except Exception:
        # Fall back to auto-generated English captions.
        transcript = transcript_list.find_generated_transcript(["en"])

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