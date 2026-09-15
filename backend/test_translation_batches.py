from app.services.translation_service import create_batches, translate_batch


test_segments = [
    {
        "text": "This is the first transcript segment.",
        "start": 0.0,
        "duration": 2.0,
    },
    {
        "text": "This is the second transcript segment.",
        "start": 2.0,
        "duration": 2.5,
    },
    {
        "text": "This is the third transcript segment.",
        "start": 4.5,
        "duration": 3.0,
    },
    {
        "text": "This is the fourth transcript segment.",
        "start": 7.5,
        "duration": 2.0,
    },
]


batches = create_batches(
    test_segments,
    max_chars=80
)


print("Translation batching + Gemini test")
print("-" * 60)

print("Total batches:", len(batches))


for batch_number, batch in enumerate(batches, start=1):

    print(f"\nBatch {batch_number}")
    print("-" * 60)

    result = translate_batch(
        batch,
        "English"
    )

    print("Validated translations:")

    for item in result:
        print(
            f"ID: {item['id']} | "
            f"Translation: {item['translation']}"
        )