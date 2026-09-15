from youtube_transcript_api import YouTubeTranscriptApi
from app.services.translation_service import create_batches, translate_batch


VIDEO_ID = "m2Jjbr380m0"


api = YouTubeTranscriptApi()

transcript_list = api.list(VIDEO_ID)

# Find the Telugu auto-generated transcript.
transcript = next(
    transcript
    for transcript in transcript_list
    if transcript.language_code == "te"
)

fetched = transcript.fetch()


# Use only the first 4 segments for testing.
original_segments = [
    {
        "text": snippet.text,
        "start": snippet.start,
        "duration": snippet.duration,
    }
    for snippet in fetched[:4]
]


print("Transcript translation integration test")
print("-" * 60)

print("Original language:", fetched.language)
print("Language code:", fetched.language_code)
print("Test segments:", len(original_segments))


# Create batches.
batches = create_batches(
    original_segments,
    max_chars=6000
)

print("Total batches:", len(batches))


# Translate batches.
translated_segments = []

for batch_number, batch in enumerate(batches, start=1):

    print(f"\nBatch {batch_number}")
    print("-" * 60)

    translations = translate_batch(
        batch,
        fetched.language
    )

    translated_segments.extend(translations)

    for item in translations:
        print(
            f"ID: {item['id']} | "
            f"Translation: {item['translation']}"
        )


# Verify that the number of translations
# matches the number of original segments.
assert len(translated_segments) == len(original_segments)


# Map translations by segment ID.
translations_by_id = {
    item["id"]: item["translation"]
    for item in translated_segments
}


# Reconstruct English segments while preserving timestamps.
english_segments = []

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


# Verify that the final English transcript
# contains the same number of segments.
assert len(original_segments) == len(english_segments)


print("\nTimestamp preservation check")
print("-" * 60)


for index, segment in enumerate(english_segments):

    original = original_segments[index]

    print(f"\nSegment {index}")
    print("Original text :", original["text"])
    print("English text  :", segment["text"])
    print("Start         :", segment["start"])
    print("Duration      :", segment["duration"])

    # Verify timestamps were not changed during translation.
    assert segment["start"] == original["start"]
    assert segment["duration"] == original["duration"]


print("\n" + "-" * 60)
print("Integration test passed successfully!")