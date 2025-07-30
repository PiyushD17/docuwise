from typing import Dict, List, Tuple

import faiss
import numpy as np


def index_embeddings(embs: list[list[float]], metadata: list[dict]):
    if len(embs) != len(metadata):
        raise ValueError("Embeddings and metadata must have the same length")

    dim = len(embs[0])
    index = faiss.IndexFlatL2(dim)
    arr = np.array(embs, dtype="float32")
    index.add(arr)

    return index, metadata  # Return both FAISS index and metadata list


class FAISSIndexer:
    """
    indexes embeddings using FAISS for similarity search.
    """

    def __init__(self, dim: int = 1536):
        """
        Args:
            dim (int): Dimensionalit of the embedding vectors.
        """

        self.index = faiss.IndexFlatL2(dim)
        self.metadata_store: List[Dict] = []

    def add_embeddings(
        self, embeddings: List[List[float]], metadata: List[Dict]
    ) -> Tuple[int, int]:
        """
        Adds embeddings and metadata to the FAISS index.

        Args:
            embeddings (List[List[float]]): Embedding vectors.
            metadata (List[Dict]): Metadata corresponding to each vector.

        Returns:
            Tuple[int, int]: Number of vectors and metadata entries added.

        Raises:
            ValueError: If lengths don't match or inputs are empty.
        """
        if not embeddings or not metadata:
            raise ValueError("Vectors and metadata must not be empty.")
        if len(embeddings) != len(metadata):
            raise ValueError("Vectors and metadata must be of same length.")

        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata_store.extend(metadata)
        return len(embeddings), len(metadata)
