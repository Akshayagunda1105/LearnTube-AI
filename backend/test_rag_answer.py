from app.services.rag_service import (
    build_context,
    generate_rag_answer,
)


results = [
    {
        "text": (
            "Supervised learning uses labeled examples "
            "to train a model to make predictions on new data."
        ),
        "start": 8.0,
        "end": 16.0,
        "distance": 0.4,
    },
    {
        "text": (
            "Unsupervised learning works with unlabeled data "
            "and can discover hidden patterns or structures."
        ),
        "start": 16.0,
        "end": 24.0,
        "distance": 0.7,
    },
]


question = "How does supervised learning work?"


print("RAG answer generation test")
print("-" * 60)


# Build context from retrieved chunks.
context = build_context(results)


print("Question:")
print(question)


print("\nGenerating answer...")
print("-" * 60)


answer = generate_rag_answer(
    question,
    context
)


print("\nAnswer:")
print(answer)


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert isinstance(answer, str)
assert len(answer.strip()) > 0


print("\n" + "-" * 60)
print("RAG answer generation test passed successfully!")