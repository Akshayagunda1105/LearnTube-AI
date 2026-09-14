from app.services.transcript_service import fetch_transcript


video_id = "m2Jjbr380m0"

result = fetch_transcript(video_id)

print("Language:", result["language"])
print("Language code:", result["language_code"])
print("Generated:", result["is_generated"])
print("Total segments:", len(result["segments"]))

print("\nFirst 3 segments:")
print("-" * 50)

for segment in result["segments"][:3]:
    print(
        f"[{segment['start']:.2f}s] "
        f"{segment['text']}"
    )