from youtube_transcript_api import YouTubeTranscriptApi

video_id = "i_LwzRVP7bg"

api = YouTubeTranscriptApi()

transcript_list = api.list(video_id)

print("Available transcripts:")
print("-" * 50)

for transcript in transcript_list:
    print(
        f"Language: {transcript.language} | "
        f"Code: {transcript.language_code} | "
        f"Generated: {transcript.is_generated}"
    )

print("-" * 50)

transcript = transcript_list.find_transcript(["en"])
fetched = transcript.fetch()

print(f"Language: {fetched.language}")
print(f"Language code: {fetched.language_code}")
print(f"Generated: {fetched.is_generated}")
print(f"Total segments: {len(fetched)}")

print("\nFirst 5 segments:")
print("-" * 50)

for snippet in fetched[:5]:
    print(
        f"[{snippet.start:.2f}s] "
        f"{snippet.text}"
    )