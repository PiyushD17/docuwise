import os

import faiss
import numpy as np
import openai
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from openai import AzureOpenAI
from pypdf import PdfReader

load_dotenv()

# ── Common Azure settings from .env ──────────────────────────────────────────────
EMBED_API_VER = os.getenv("AZURE_OPENAI_API_VERSION")
EMBED_URL = os.getenv("AZURE_OPENAI_ENDPOINT")
EMBED_KEY = os.getenv("AZURE_OPENAI_API_KEY")
EMBED_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

CHAT_URL = os.getenv("AZURE_CHAT_OPENAI_ENDPOINT")
CHAT_KEY = os.getenv("AZURE_CHAT_OPENAI_KEY")
CHAT_MODEL = os.getenv("AZURE_CHAT_DEPLOYMENT")
CHAT_API_VER = os.getenv("AZURE_CHAT_VERSION")


# ── PDF → text pipeline ──────────────────────────────────────────────────────────
def load_pdf(path: str):
    return [page.extract_text() or "" for page in PdfReader(path).pages]


def chunk_texts(pages: list[str]):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return [chunk for pg in pages for chunk in splitter.split_text(pg)]


# ── Embeddings via per-call overrides ───────────────────────────────────────────
def embed_texts(texts: list[str]) -> np.ndarray:
    openai.api_type = "azure"
    openai.api_base = EMBED_URL
    openai.api_version = EMBED_API_VER
    openai.api_key = EMBED_KEY

    resp = openai.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    # resp.data items have .embedding
    return np.array([item.embedding for item in resp.data], dtype="float32")


def build_index(embs: np.ndarray):
    idx = faiss.IndexFlatL2(embs.shape[1])
    idx.add(embs)
    return idx


# ── Retrieval ───────────────────────────────────────────────────────────────────
def retrieve(question: str, chunks: list[str], idx, k=3):
    openai.api_type = "azure"
    openai.api_base = EMBED_URL
    openai.api_version = EMBED_API_VER
    openai.api_key = EMBED_KEY
    resp = openai.embeddings.create(
        model=EMBED_MODEL,
        input=[question],
    )
    q_emb = np.array([resp.data[0].embedding], dtype="float32")
    D, L = idx.search(q_emb, k=k)
    return [{"chunk": chunks[i], "dist": float(D[0][j])} for j, i in enumerate(L[0])]


# ── ChatCompletion via per-call overrides ───────────────────────────────────────
def ask_chat(question: str, contexts: list[str]):
    openai.api_type = "azure"
    openai.api_base = CHAT_URL
    openai.api_version = CHAT_API_VER
    openai.api_key = CHAT_KEY
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"Context:\n\n{''.join(contexts)}\n\nQuestion: {question}\nAnswer:",
        },
    ]
    client = AzureOpenAI(
        api_version=CHAT_API_VER,
        azure_endpoint=CHAT_URL,
        api_key=CHAT_KEY,
    )
    response = client.chat.completions.create(
        messages=messages, max_tokens=4096, temperature=1.0, top_p=1.0, model=CHAT_MODEL
    )
    # resp = openai.chat.completions.create(
    #     model=CHAT_MODEL,
    #     messages=messages,
    # )
    return response.choices[0].message.content


# ── End-to-end Demo ─────────────────────────────────────────────────────────────
def main():
    pages = load_pdf("data/sample.pdf")
    chunks = chunk_texts(pages)
    embs = embed_texts(chunks)
    idx = build_index(embs)

    question = "What is the main topic of this document?"
    topk = retrieve(question, chunks, idx, k=3)
    # print("Retrieved chunks:")
    # for e in topk:
    #     print(f" • [{e['dist']:.2f}] {e['chunk'][:100]}…")

    answer = ask_chat(question, [e["chunk"] for e in topk])
    print("\nAnswer:\n", answer)


if __name__ == "__main__":
    main()
