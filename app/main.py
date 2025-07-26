import os
from pathlib import Path

import faiss
import numpy as np
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from langchain.text_splitter import CharacterTextSplitter
from pypdf import PdfReader

load_dotenv()  # load Azure creds from .env

# Azure OpenAI config
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

app = FastAPI()
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)


def load_pdf(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    return [page.extract_text() or "" for page in reader.pages]


def chunk_texts(pages: list[str]) -> list[str]:
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return [chunk for page in pages for chunk in splitter.split_text(page)]


def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = openai.embeddings.create(model=DEPLOYMENT_NAME, input=texts)
    return [d.embedding for d in resp.data]


def index_embeddings(embs: list[list[float]]):
    dim = len(embs[0])
    idx = faiss.IndexFlatL2(dim)
    arr = np.array(embs, dtype="float32")
    idx.add(arr)
    return idx


@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF allowed")
    path = UPLOAD_DIR / file.filename
    with open(path, "wb") as f:
        f.write(await file.read())

    # Pipeline
    pages = load_pdf(path)
    chunks = chunk_texts(pages)
    embeddings = embed_texts(chunks)
    index = index_embeddings(embeddings)

    # Sample lookup (first chunk → top 3 neighbors)
    D, L = index.search(np.array([embeddings[0]], dtype="float32"), k=3)
    return {
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "embeddings": len(embeddings),
        "nn_indices": L[0].tolist(),
        "nn_distances": D[0].tolist(),
    }
