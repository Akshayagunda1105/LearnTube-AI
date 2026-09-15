from youtube_transcript_api import YouTubeTranscriptApi
from app.services.translation_service import translate_text


video_id = "m2Jjbr380m0"

api = YouTubeTranscriptApi()
transcript_list = api.list(video_id)

# Find the available transcript.
try:
    transcript = next(
        transcript
        for transcript in transcript_list
        if not transcript.is_generated
    )
except StopIteration:
    transcript = next(
        transcript
        for transcript in transcript_list
        if transcript.is_generated
    )

fetched = transcript.fetch()

segments = [
    {
        "text": snippet.text,
        "start": snippet.start,
        "duration": snippet.duration,
    }
    for snippet in fetched[:3]
]

print("Translation integration test")
print("-" * 60)

print("Original language:", fetched.language)
print("Language code:", fetched.language_code)
print("Generated:", fetched.is_generated)
print()

for segment in segments:
    english_text = translate_text(
        segment["text"],
        fetched.language
    )

    print(f"[{segment['start']:.2f}s]")
    print("Original :", segment["text"])
    print("English  :", english_text)
    print("-" * 60)