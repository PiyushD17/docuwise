from typing import Any, Dict, List, Tuple

import faiss
import numpy as np


class FAISSIndexer:
    """
    indexes embeddings using FAISS for similarity search.
    """

    def __init__(self, dim: int = 1536):
        """
        Args:
            dim (int): Dimensionality of the embedding vectors.
        """

        self.index = faiss.IndexFlatL2(dim)
        self.metadata_store: List[Dict[str, Any]] = []

    def add_embeddings(
        self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Adds embeddings and metadata to the FAISS index.

        Args:
            embeddings (List[List[float]]): Embedding vectors.
            metadata (List[Dict[str, Any]]): Metadata corresponding to each vector.

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
