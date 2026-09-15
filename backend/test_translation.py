from app.services.translation_service import translate_text


test_segments = [
    {
        "text": "ఓ వీడితో ఎందుకు వచ్చాను గొడవ ఎంతో కొంత",
        "start": 1.92,
    },
    {
        "text": "వేస్తే బెటర్",
        "start": 4.88,
    },
    {
        "text": "[నిట్టూర్పులు]",
        "start": 9.82,
    },
]


print("Testing Telugu → English translation")
print("-" * 60)

for segment in test_segments:
    translated_text = translate_text(
        segment["text"],
        "Telugu"
    )

    print(f"[{segment['start']:.2f}s]")
    print("Original :", segment["text"])
    print("English  :", translated_text)
    print("-" * 60)