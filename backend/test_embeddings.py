from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()


text = """
Machine learning allows computers to learn patterns
from data and make predictions.
"""


print("Gemini embedding test")
print("-" * 60)


response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text
)


embedding = response.embeddings[0].values


print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First 10 values:", embedding[:10])


assert isinstance(embedding, list)
assert len(embedding) > 0


print("\n" + "-" * 60)
print("Embedding test passed successfully!")