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
