import faiss
import numpy as np


print("FAISS similarity search test")
print("-" * 60)


# --------------------------------------------------
# Create sample vectors
# --------------------------------------------------

vectors = np.array(
    [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.9, 0.1, 0.0],
    ],
    dtype="float32",
)


print("Number of vectors:", len(vectors))
print("Vector dimension:", vectors.shape[1])


# --------------------------------------------------
# Create FAISS index
# --------------------------------------------------

dimension = vectors.shape[1]

index = faiss.IndexFlatL2(dimension)

print("\nFAISS index created")
print("Index dimension:", index.d)


# --------------------------------------------------
# Add vectors to the index
# --------------------------------------------------

index.add(vectors)

print("Vectors stored in index:", index.ntotal)


# --------------------------------------------------
# Create a query vector
# --------------------------------------------------

query = np.array(
    [
        [0.88, 0.12, 0.0]
    ],
    dtype="float32",
)


# --------------------------------------------------
# Search for the 2 most similar vectors
# --------------------------------------------------

distances, indices = index.search(
    query,
    2
)


print("\nSearch results")
print("-" * 60)

print("Nearest vector indices:", indices[0])
print("Distances:", distances[0])


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert index.ntotal == 3

assert indices.shape == (1, 2)
assert distances.shape == (1, 2)


# The query should be closest to vector 2:
#
# Query:
# [0.88, 0.12, 0.0]
#
# Vector 2:
# [0.9, 0.1, 0.0]
#
# These vectors are very similar.

assert indices[0][0] == 2


# The first result should have a smaller
# distance than the second result.

assert distances[0][0] < distances[0][1]


print("\n" + "-" * 60)
print("FAISS similarity search test passed successfully!")