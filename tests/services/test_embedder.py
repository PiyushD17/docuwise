from unittest.mock import MagicMock, patch

import pytest

from app.services.embedder import TextEmbedder


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "docuwise-embeddings")


def test_init_uses_env_variable(mock_env):
    embedder = TextEmbedder()
    assert embedder.deployment == "docuwise-embeddings"


def test_init_raises_without_deployment(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", raising=False)
    with pytest.raises(ValueError):
        TextEmbedder()


@patch("app.services.embedder.openai.Embedding.create")
def test_embed_returns_embeddings(mock_env):
    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1, 0.2]

    mock_embedding2 = MagicMock()
    mock_embedding2.embedding = [0.3, 0.4]

    mock_response = MagicMock()
    mock_response.data = [mock_embedding, mock_embedding2]

    mock_client = MagicMock()
    mock_client.create.return_value = mock_response

    embedder = TextEmbedder(embedding_client=mock_client)
    result = embedder.embed(["Hello world", "Test embedding"])

    assert result == [[0.1, 0.2], [0.3, 0.4]]
    mock_client.create.assert_called_once()


@patch(
    "app.services.embedder.openai.Embedding.create", side_effect=Exception("API error")
)
def test_embed_raises_on_failure(mock_env):
    mock_client = MagicMock()
    mock_client.create.side_effect = Exception("API error")

    embedder = TextEmbedder(embedding_client=mock_client)

    with pytest.raises(RuntimeError, match=r"Embedding failed: API error"):
        embedder.embed(["fail this"])
