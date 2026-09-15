from app.services.rag_service import build_context


results = [
    {
        "text": (
            "Supervised learning uses labeled examples "
            "to train a model."
        ),
        "start": 8.0,
        "end": 16.0,
        "distance": 0.4,
    },
    {
        "text": (
            "Unsupervised learning discovers patterns "
            "in unlabeled data."
        ),
        "start": 16.0,
        "end": 24.0,
        "distance": 0.7,
    },
]


print("RAG context builder test")
print("-" * 60)


context = build_context(results)


print("Generated context")
print("-" * 60)
print(context)


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert isinstance(context, str)
assert len(context.strip()) > 0

for result in results:

    assert result["text"] in context
    assert str(result["start"]) in context
    assert str(result["end"]) in context


assert "Source 1" in context
assert "Source 2" in context


print("\n" + "-" * 60)
print("RAG context builder test passed successfully!")