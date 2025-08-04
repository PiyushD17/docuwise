import os
from typing import Any, List, Optional

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")


class TextEmbedder:
    """
    A class to generate embeddings for a list of text chunks using Azure OpenAI.
    """

    def __init__(self, deployment: Optional[str] = None, embedding_client: Any = None):
        """
        Initialize the embedder with an Azure deployment name.

        Args:
            deployment (str): Azure deployment name. If None, loaded from env var.
        """

        self.deployment = deployment or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        if not self.deployment:
            raise ValueError("Deployment name must be provided or set in environment.")
        # Injectable client, default is openai.Embedding
        self.embedding_client = embedding_client or openai.embeddings

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of text chunks.

        Args:
            texts (List[str]): List of text chunks to embed.

        Returns:
            List[List[float]]: Embedding vectors for each chunk.
        """

        try:
            if not self.deployment:
                raise ValueError(
                    "Deployment name must be provided or set in environment."
                )
            response = self.embedding_client.create(
                model=str(self.deployment), input=texts
            )
            return [d.embedding for d in response.data]
            # return [item["embedding"] for item in response["data"]]
        except Exception as e:
            raise RuntimeError(f"Embedding failed: {e}")
