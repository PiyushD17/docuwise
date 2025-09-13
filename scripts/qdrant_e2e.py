#!/usr/bin/env python3
"""
Qdrant E2E smoke test using REST API.

Env vars:
  API  -> base URL to Qdrant (e.g. https://your-qdrant-endpoint:6333)
  KEY  -> Qdrant API key
  COL  -> (optional) collection name (default: quicktest)
  DIM  -> (optional) vector size (default: 4 for toy test; use 1536/3072 in prod)
  DIST -> (optional) distance metric (Cosine|Euclid|Dot) default: Cosine
  RESET-> (optional) if "1", drop collection first

Example:
  export API="https://qdrant.example.com"
  export KEY="xxxxxxxx"
  python qdrant_e2e.py
"""

import json
import os
import random
import sys
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()
API = os.environ["QDRANT_URL"].rstrip("/")
KEY = os.environ["QDRANT_API_KEY"]
COL = os.environ.get("COL", "quicktest")
DIM = int(os.environ.get("DIM", "4"))
DIST = os.environ.get("DIST", "Cosine")
# RESET = os.environ.get("RESET", "0") == "1"
RESET = "1"

if not API or not KEY:
    print("ERROR: Please set API and KEY environment variables.", file=sys.stderr)
    sys.exit(1)

S = requests.Session()
S.headers.update({"api-key": KEY, "Content-Type": "application/json"})


def pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def get(path: str) -> Dict[str, Any]:
    r = S.get(f"{API}{path}")
    r.raise_for_status()
    return r.json()  # type: ignore


def put(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = S.put(f"{API}{path}", json=payload)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        # Print server error body for debugging
        print(f"PUT {path} failed [{r.status_code}]: {r.text}", file=sys.stderr)
        raise
    return r.json()  # type: ignore


def post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = S.post(f"{API}{path}", json=payload)
    r.raise_for_status()
    return r.json()  # type: ignore


def delete(path: str) -> Dict[str, Any]:
    r = S.delete(f"{API}{path}")
    r.raise_for_status()
    return r.json()  # type: ignore


def readyz() -> None:
    print("==> /readyz")
    r = S.get(f"{API}/readyz")
    r.raise_for_status()
    print("OK")


def maybe_drop_collection() -> None:
    if RESET:
        print(f"==> Dropping collection '{COL}'")
        try:
            resp = delete(f"/collections/{COL}")
            print(pretty(resp))
        except requests.HTTPError as e:
            # If not found, that’s fine
            if e.response is not None and e.response.status_code == 404:
                print("Collection not found; nothing to drop.")
            else:
                raise


def ensure_collection() -> None:
    print(f"==> Creating collection '{COL}' (size={DIM}, distance={DIST}) if missing")
    payload = {"vectors": {"size": DIM, "distance": DIST}}
    resp = put(f"/collections/{COL}", payload)
    print(pretty(resp))
    print("==> Get collection info")
    info = get(f"/collections/{COL}")
    print(pretty(info))


def create_indexes() -> None:
    print(
        "==> Creating payload indexes (doc_id keyword, page integer, text full-text if supported)"
    )
    # Create the ones we definitely need first
    idx_ops = [
        {"field_name": "doc_id", "field_schema": "keyword"},
        {"field_name": "page", "field_schema": "integer"},
    ]

    for op in idx_ops:
        try:
            resp = put(f"/collections/{COL}/index", op)
            print(pretty(resp))
        except requests.HTTPError as e:
            # 409 = exists already
            if e.response is not None and e.response.status_code == 409:
                print(f"Index already exists for '{op['field_name']}', skipping.")
            else:
                raise

    # Try full-text only if the server supports it
    text_op = {"field_name": "text", "field_schema": {"type": "text"}}
    try:
        resp = put(f"/collections/{COL}/index", text_op)
        print(pretty(resp))
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code in (400, 404, 501):
            print(
                "Full-text index not supported on this Qdrant version/build — continuing without it."
            )
        elif e.response is not None and e.response.status_code == 409:
            print("Full-text index already exists, skipping.")
        else:
            raise


def random_unit_vector(dim: int) -> List[float]:
    # Simple random vector; not strictly unit-normalized to avoid numpy dep
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]


def upsert_demo_points() -> None:
    print("==> Upserting demo points")

    # If DIM=4, use your toy vectors; otherwise generate random vectors of length DIM
    if DIM == 4:
        points = [
            {
                "id": 1,
                "vector": [0.1, 0.2, 0.3, 0.4],
                "payload": {
                    "doc_id": "demo_a",
                    "page": 1,
                    "text": "hello world",
                    "source": "a",
                },
            },
            {
                "id": 2,
                "vector": [0.9, 0.8, 0.7, 0.6],
                "payload": {
                    "doc_id": "demo_b",
                    "page": 2,
                    "text": "lorem ipsum",
                    "source": "b",
                },
            },
            {
                "id": 3,
                "vector": [0.2, 0.1, 0.0, -0.1],
                "payload": {
                    "doc_id": "demo_a",
                    "page": 3,
                    "text": "qdrant e2e",
                    "source": "a",
                },
            },
        ]
    else:
        points = []
        for i in range(1, 6):
            points.append(
                {
                    "id": i,
                    "vector": random_unit_vector(DIM),
                    "payload": {
                        "doc_id": f"demo_{'a' if i % 2 else 'b'}",
                        "page": i,
                        "text": f"chunk {i}",
                        "source": "a" if i % 2 else "b",
                    },
                }
            )

    resp = put(f"/collections/{COL}/points", {"points": points})
    print(pretty(resp))


def simple_search() -> None:
    print("==> Vector search (no filter)")
    if DIM == 4:
        query = [0.1, 0.2, 0.3, 0.4]
    else:
        query = random_unit_vector(DIM)

    resp = post(
        f"/collections/{COL}/points/search",
        {"vector": query, "limit": 3, "with_payload": True, "with_vector": False},
    )
    print(pretty(resp))


def filtered_search() -> None:
    print("==> Vector search with a payload filter (source == 'a')")
    if DIM == 4:
        query = [0.1, 0.2, 0.3, 0.4]
    else:
        query = random_unit_vector(DIM)

    resp = post(
        f"/collections/{COL}/points/search",
        {
            "vector": query,
            "limit": 5,
            "filter": {"must": [{"key": "source", "match": {"value": "a"}}]},
            "with_payload": True,
        },
    )
    print(pretty(resp))


def scroll_points() -> None:
    print("==> Scroll points (list)")
    resp = post(
        f"/collections/{COL}/points/scroll",
        {"limit": 5, "with_payload": True, "with_vector": False},
    )
    print(pretty(resp))


def count_points() -> int:
    print("==> Count points")
    resp = post(f"/collections/{COL}/points/count", {"exact": True})
    print(pretty(resp))
    return resp.get("result", {}).get("count", 0)  # type: ignore


def delete_point(point_id: int) -> None:
    print(f"==> Delete point id={point_id}")
    resp = post(f"/collections/{COL}/points/delete", {"points": [point_id]})
    print(pretty(resp))


def main() -> None:
    print("=== Qdrant E2E Smoke Test ===")
    readyz()
    maybe_drop_collection()
    ensure_collection()
    create_indexes()
    upsert_demo_points()
    simple_search()
    filtered_search()
    scroll_points()
    before = count_points()
    if before > 0:
        delete_point(1)
        after = count_points()
        print(f"Count before={before}, after deleting id=1 -> {after}")
    print("=== DONE ===")


if __name__ == "__main__":
    main()
