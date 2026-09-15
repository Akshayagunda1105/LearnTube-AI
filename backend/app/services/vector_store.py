import faiss
import numpy as np


class VectorStore:
    """
    Store RAG chunk embeddings in a FAISS index
    and retrieve the most similar chunks.
    """

    def __init__(self, dimension):
        """
        Create an empty FAISS index.

        dimension:
            Number of values in each embedding vector.
        """

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

        # Keep the original RAG chunks separately.
        # FAISS only stores vectors and returns their indices.
        self.chunks = []


    def add_chunks(self, chunks):
        """
        Add RAG chunks and their embeddings to FAISS.
        """

        if not chunks:
            raise ValueError(
                "Chunks cannot be empty"
            )

        embeddings = np.array(
            [
                chunk["embedding"]
                for chunk in chunks
            ],
            dtype="float32",
        )

        # Verify that the embedding dimensions
        # match the FAISS index dimension.
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                "Embedding dimension does not match "
                "FAISS index dimension"
            )

        # Add vectors to FAISS.
        self.index.add(embeddings)

        # Store the corresponding chunks.
        self.chunks.extend(chunks)


    def search(self, query_embedding, top_k=3):
        """
        Search for the most similar RAG chunks.

        Returns the matching chunks together with
        their similarity distances.
        """

        if self.index.ntotal == 0:
            raise ValueError(
                "Vector store is empty"
            )

        query_vector = np.array(
            [query_embedding],
            dtype="float32",
        )

        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                "Query embedding dimension does not "
                "match FAISS index dimension"
            )

        # We cannot retrieve more results than
        # the number of stored vectors.
        top_k = min(
            top_k,
            self.index.ntotal
        )

        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):
            chunk = self.chunks[index]

            results.append(
                {
                    "text": chunk["text"],
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "distance": float(distance),
                }
            )

        return results