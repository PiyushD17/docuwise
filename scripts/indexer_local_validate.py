#!/usr/bin/env python3
import math
import os
import socket
import time
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

# --- deps / env ---
from dotenv import load_dotenv
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

load_dotenv()
socket.setdefaulttimeout(15)
# ============= Config =============
# Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
EMBED_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")

# Qdrant
QDRANT_URL = os.environ["QDRANT_URL"].strip().rstrip("/")
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

COLLECTION = os.environ.get("QDRANT_COLLECTION", "docuwise-dev-validate")
EMBED_DIM = int(os.environ.get("EMBED_DIM", "1536"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "32"))
RESET = os.environ.get("RESET", "0") == "1"  # True once for clean recreate

# Optional PDF
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

# ============= HTTP / Clients =============
# More reliable HTTPX transport on Windows/VPN/corp nets
transport = httpx.HTTPTransport(retries=3)
client_kwargs = {
    "timeout": 60.0,
    "verify": True,
    "transport": transport,
    "http2": False,  # helps in some environments
    "trust_env": True,  # pick up system proxies if any
}


def make_qdrant_client() -> QdrantClient:
    # Prefer URL constructor
    try:
        return QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            prefer_grpc=False,
            timeout=60.0,
            trust_env=True,
            client_kwargs=client_kwargs,
        )
    except Exception:
        pass
    # Fallback: host/port form

    p = urlparse(QDRANT_URL)
    return QdrantClient(
        host=p.hostname,
        port=p.port or (443 if p.scheme == "https" else 80),
        https=(p.scheme == "https"),
        api_key=QDRANT_API_KEY,
        prefer_grpc=False,
        timeout=60.0,
        trust_env=True,
    )


def warm_up(url: str, api_key: str, tries: int = 10, delay: int = 5) -> None:
    headers = {"api-key": api_key}
    for i in range(1, tries + 1):
        try:
            r = httpx.get(f"{url}/readyz", headers=headers, timeout=10)
            if r.status_code == 200:
                print("Qdrant is ready.")
                return
        except Exception:
            pass
        print(f"Waiting for Qdrant to be ready… attempt {i}/{tries}")
        time.sleep(delay)
    raise RuntimeError("Qdrant did not become ready in time.")


warm_up(QDRANT_URL, QDRANT_API_KEY)

# Single client
qdrant = make_qdrant_client()

# Azure OpenAI client
aoai = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=EMBED_API_VERSION,
)


# ============= Helpers =============
def chunk_text(text: str, max_tokens: int = 400) -> List[str]:
    raw = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: List[str] = []
    cur_len = 0
    cur: List[str] = []
    for p in raw:
        est = max(1, math.ceil(len(p.split()) * 0.75))
        if cur and cur_len + est > max_tokens:
            chunks.append(" ".join(cur))
            cur, cur_len = [], 0
        cur.append(p)
        cur_len += est
    if cur:
        chunks.append(" ".join(cur))
    return chunks[:200]


def extract_pdf_text(path: str) -> str:
    if not PdfReader:
        raise RuntimeError(
            "pypdf not installed. `pip install pypdf` or set a sample instead."
        )
    reader = PdfReader(path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])


def collection_exists_retry(name: str, tries: int = 3, delay: float = 2.0) -> bool:
    for i in range(1, tries + 1):
        try:
            return qdrant.collection_exists(name)  # type: ignore
        except (ResponseHandlingException, socket.gaierror, httpx.ConnectError) as e:  # type: ignore[name-defined]
            if i == tries:
                raise
            print(f"collection_exists failed ({e}); retry {i}/{tries} after {delay}s…")
            time.sleep(delay)
    return False


def embed_texts(texts: List[str]) -> List[List[float]]:
    resp = aoai.embeddings.create(model=EMBED_DEPLOYMENT, input=texts)
    data_sorted = sorted(resp.data, key=lambda d: d.index)  # keep input order
    return [d.embedding for d in data_sorted]


# ============= Collection / Indexes =============
def ensure_collection(reset: bool = False) -> None:
    if reset and collection_exists_retry(COLLECTION):
        qdrant.delete_collection(COLLECTION)
        print(f"Deleted existing collection: {COLLECTION}")

    if collection_exists_retry(COLLECTION):
        info = qdrant.get_collection(COLLECTION)
        current_dim = info.dict()["config"]["params"]["vectors"]["size"]
        if int(current_dim) != EMBED_DIM:
            print(
                f"Collection exists with dim={current_dim}, expected {EMBED_DIM}. Recreating…"
            )
            qdrant.delete_collection(COLLECTION)
            qdrant.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
            )
            print(f"Recreated collection: {COLLECTION}")
        else:
            print(f"Collection {COLLECTION} OK (dim={current_dim}).")
        return

    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )
    print(f"Created collection: {COLLECTION}")


def try_create_indexes() -> None:
    """Create keyword/int indexes if supported; skip quietly if not."""
    try:
        qdrant.create_payload_index(
            COLLECTION, field_name="doc_id", field_schema=PayloadSchemaType.KEYWORD
        )
        qdrant.create_payload_index(
            COLLECTION, field_name="chunk_index", field_schema=PayloadSchemaType.INTEGER
        )
        print("Created payload indexes: doc_id(keyword), chunk_index(integer).")
    except Exception as e:
        print(f"Index creation skipped or partial ({e}). Continuing…")


# ============= Ingest =============
def index_text_blocks(blocks: List[str], doc_id: str) -> None:
    ensure_collection(reset=RESET)
    try_create_indexes()

    for idx in range(0, len(blocks), BATCH_SIZE):
        sub = blocks[idx : idx + BATCH_SIZE]
        vecs = embed_texts(sub)

        points: List[PointStruct] = []
        for j, (text, vec) in enumerate(zip(sub, vecs)):
            pid = str(uuid.uuid4())  # valid UUID string
            payload = {"doc_id": doc_id, "chunk_index": idx + j, "text": text}
            points.append(PointStruct(id=pid, vector=vec, payload=payload))

        r = qdrant.upsert(collection_name=COLLECTION, points=points, wait=True)
        status = getattr(r, "status", None)
        print(
            f"Upserted {len(points)} points (batch starting at {idx}), status={status or 'ok'}"
        )

    print(f"Indexed {len(blocks)} chunks into {COLLECTION}")


# ============= Search =============
def search(
    query: str, top_k: int = 5, only_doc_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    vec = embed_texts([query])[0]

    qfilter: Optional[Filter] = None
    if only_doc_id:
        qfilter = Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=only_doc_id))]
        )

    # Older qdrant-client uses `query_filter`; newer uses `filter`.
    kwargs: Dict[str, Any] = dict(
        collection_name=COLLECTION,
        query=vec,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )
    if qfilter is not None:
        kwargs["query_filter"] = qfilter

    try:
        res = qdrant.query_points(**kwargs)
    except AssertionError:
        # Fallback for newer clients
        if "query_filter" in kwargs:
            kwargs["filter"] = kwargs.pop("query_filter")
        res = qdrant.query_points(**kwargs)

    hits = res.points
    results: List[Dict[str, Any]] = []
    for h in hits:
        payload = h.payload or {}
        results.append(
            {
                "id": h.id,
                "score": float(h.score),
                "doc_id": payload.get("doc_id"),
                "chunk_index": payload.get("chunk_index"),
                "text": (payload.get("text") or "")[:200],
            }
        )
    return results


# ============= Main =============
if __name__ == "__main__":
    # Choose content: sample strings OR ./data/sample.pdf
    sample_blocks = [
        "DocuWise is a private RAG service that indexes PDFs and answers questions.",
        "It uses Azure OpenAI for embeddings and GPT for answers.",
        "Qdrant stores the vectors; Event Hub will decouple ingestion later.",
    ]
    # pdf_path = os.path.join("data", "sample.pdf")
    blocks = sample_blocks
    # if os.path.exists(pdf_path):
    #     text = extract_pdf_text(pdf_path)
    #     blocks = chunk_text(text, max_tokens=350)
    #     print(f"PDF chunks: {len(blocks)}")
    # else:
    #     blocks = sample_blocks

    # Ingest
    doc_id = str(uuid.uuid4())[:8]
    index_text_blocks(blocks, doc_id)

    # Query (filtered to the document we just ingested)
    q = "Where are the vectors stored?"
    res = search(q, top_k=3, only_doc_id=doc_id)
    print(f"\nQuery: {q}")
    for r in res:
        print(f"[{r['score']:.3f}] {r['id']} :: {r['text']}")
