import os

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")


def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = openai.embeddings.create(model=DEPLOYMENT_NAME, input=texts)
    return [d.embedding for d in resp.data]
