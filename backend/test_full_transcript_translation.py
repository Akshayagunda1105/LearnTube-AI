from app.services.transcript_service import fetch_transcript


VIDEO_ID = "m2Jjbr380m0"


print("Full transcript translation test")
print("-" * 60)

result = fetch_transcript(VIDEO_ID)

print("Original language:", result["language"])
print("Language code:", result["language_code"])
print("Generated:", result["is_generated"])

print("\nOriginal segments:", len(result["original_segments"]))
print("English segments:", len(result["english_segments"]))

print("\nFirst 5 translated segments")
print("-" * 60)

for index in range(5):
    original = result["original_segments"][index]
    english = result["english_segments"][index]

    print(f"\nSegment {index}")
    print("Original :", original["text"])
    print("English  :", english["text"])
    print("Start    :", english["start"])
    print("Duration :", english["duration"])

    assert original["start"] == english["start"]
    assert original["duration"] == english["duration"]

print("\n" + "-" * 60)
print("Full transcript translation test passed!")