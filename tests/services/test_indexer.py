# tests/services/test_indexer.py

import pytest

from app.services.indexer import FAISSIndexer


def test_indexer_adds_embeddings_and_metadata():
    embeddings = [
        [0.1, 0.2, 0.3, 0.4],
        [0.4, 0.3, 0.2, 0.1],
    ]
    metadata = [
        {"filename": "sample.pdf", "chunk_id": 0},
        {"filename": "sample.pdf", "chunk_id": 1},
    ]
    indexer = FAISSIndexer(dim=4)
    num_vectors, num_metadata = indexer.add_embeddings(embeddings, metadata)

    assert num_vectors == 2
    assert num_metadata == 2
    assert indexer.index.ntotal == 2
    assert indexer.metadata_store == metadata


def test_indexer_empty_input():
    indexer = FAISSIndexer(dim=4)
    with pytest.raises(ValueError):
        indexer.add_embeddings([], [])
