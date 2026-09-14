from youtube_transcript_api import YouTubeTranscriptApi


video_id = "i_LwzRVP7bg"

api = YouTubeTranscriptApi()
transcript_list = api.list(video_id)

print("Testing manual transcript:")
print("-" * 50)

try:
    manual = transcript_list.find_manually_created_transcript(["en"])
    print("Manual transcript found")
    print("Language:", manual.language)
    print("Generated:", manual.is_generated)
except Exception as error:
    print("Manual transcript not found")
    print("Error:", error)


print("\nTesting auto-generated transcript:")
print("-" * 50)

try:
    generated = transcript_list.find_generated_transcript(["en"])
    print("Auto-generated transcript found")
    print("Language:", generated.language)
    print("Generated:", generated.is_generated)
except Exception as error:
    print("Auto-generated transcript not found")
    print("Error:", error)