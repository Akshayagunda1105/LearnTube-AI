from youtube_transcript_api import YouTubeTranscriptApi

video_id = "m2Jjbr380m0"

api = YouTubeTranscriptApi()

transcript_list = api.list(video_id)

print("Available transcripts:")
print("-" * 60)

for transcript in transcript_list:
    transcript_type = (
        "Generated" if transcript.is_generated else "Manual"
    )

    print(
        f"Language: {transcript.language} | "
        f"Code: {transcript.language_code} | "
        f"Type: {transcript_type}"
    )

print("-" * 60)