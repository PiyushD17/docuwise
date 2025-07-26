import os

import openai
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from pypdf import PdfReader

load_dotenv()

# ── 1) Azure OpenAI Configuration ────────────────────────────────────────────────
openai.api_type = "azure"
openai.api_base = os.getenv(
    "AZURE_OPENAI_API_BASE"
)  # e.g. https://<resource>.openai.azure.com
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # e.g. "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")  # your Key1
EMBED_MODEL = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]


# ── 2) PDF Loading ───────────────────────────────────────────────────────────────
def load_pdf(path: str) -> list[str]:
    reader = PdfReader(path)
    return [page.extract_text() or "" for page in reader.pages]


# ── 3) Text Chunking ─────────────────────────────────────────────────────────────
def chunk_texts(pages: list[str]) -> list[str]:
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return [chunk for page in pages for chunk in splitter.split_text(page)]


# ── 4) Embedding Call (from cookbook) ────────────────────────────────────────────
def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = openai.embeddings.create(model=EMBED_MODEL, input=texts)
    # resp.data is a list of items; each item.embedding is the vector
    return [
        item["embedding"] if isinstance(item, dict) else item.embedding
        for item in resp.data
    ]


# ── 5) Putting it all together ──────────────────────────────────────────────────
def main():
    # Load & chunk
    pages = load_pdf("data/sample.pdf")
    print(f"Loaded {len(pages)} pages")
    chunks = chunk_texts(pages)
    print(f"Split into {len(chunks)} chunks")

    # Embed
    embeddings = embed_texts(chunks)
    print(f"Generated {len(embeddings)} embeddings; vector dim = {len(embeddings[0])}")


if __name__ == "__main__":
    main()
