#!/usr/bin/env python
"""
DocuWise Ingest E2E (tailored to your API, mypy-clean)

Flow:
  - GET /health
  - POST /api/upload (multipart/form-data; field 'file')
  - POST /api/ingest?filename=<saved_as>
  - Assert: 'message' == 'Ingestion successful' and chunks_ingested > 0
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time
from typing import Any, Dict, NoReturn

import requests

ROOT: str = os.getenv("ROOT_URL", "http://localhost:8000").rstrip("/")
SAMPLE_PATH: str = os.getenv("SAMPLE_PATH", "data/sample.pdf")
UPLOAD_EP: str = os.getenv("UPLOAD_EP", "/api/upload")
INGEST_EP: str = os.getenv("INGEST_EP", "/api/ingest")

SAMPLE = pathlib.Path(SAMPLE_PATH)


def die(msg: str, code: int = 1) -> NoReturn:
    print(f"❌ {msg}")
    sys.exit(code)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def main() -> None:
    print(f"ROOT: {ROOT}")
    # 1) health
    print("🔎 Health…")
    try:
        r: requests.Response = requests.get(f"{ROOT}/health", timeout=8)
        r.raise_for_status()
        body: Dict[str, Any] = r.json()  # types-requests provides stubs
        assert body.get("status") == "ok"
        ok("API healthy")
    except Exception as e:
        die(f"Health failed: {e}")

    # 2) ensure sample exists & looks like a PDF
    if not SAMPLE.exists():
        die(f"Sample PDF not found at {SAMPLE}")
    with open(SAMPLE, "rb") as f:
        head = f.read(5)
    if not head.startswith(b"%PDF"):
        print("⚠️  sample.pdf does not start with %PDF — server may reject it.")

    # 3) upload
    upload_url = f"{ROOT}{UPLOAD_EP}"
    print(f"📤 Uploading to {upload_url} …")
    with open(SAMPLE, "rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        r = requests.post(upload_url, files=files, timeout=60)
    if not r.ok:
        die(f"Upload failed: {r.status_code} {r.text}")
    try:
        up: Dict[str, Any] = r.json()
    except Exception:
        die(f"Upload returned non-JSON: {r.text[:200]}")

    print("📄 Upload response:")
    print(json.dumps(up, indent=2, ensure_ascii=False))

    saved_as = up.get("saved_as") or up.get("filename")
    if not isinstance(saved_as, str):
        die("Upload response did not include 'saved_as' (or 'filename').")

    # 4) ingest
    ingest_url = f"{ROOT}{INGEST_EP}"
    params: Dict[str, str] = {"filename": saved_as}
    print(f"⚙️  Ingesting via {ingest_url} ? {params}")
    t0 = time.time()
    r = requests.post(ingest_url, params=params, timeout=120)
    dt = time.time() - t0
    if not r.ok:
        die(f"Ingest failed: {r.status_code} {r.text}")

    try:
        ing: Dict[str, Any] = r.json()
    except Exception:
        die(f"Ingest returned non-JSON: {r.text[:200]}")

    print("📦 Ingest response:")
    print(json.dumps(ing, indent=2, ensure_ascii=False))

    # 5) assertions
    msg = str(ing.get("message", "")).lower()
    chunks_val = ing.get("chunks_ingested", 0)
    try:
        chunks = int(chunks_val)
    except Exception:
        chunks = -1

    if "ingestion successful" not in msg or chunks <= 0:
        die(
            f"Ingest did not confirm success; message={ing.get('message')} chunks_ingested={chunks}"
        )

    ok(f"Ingest successful in {dt:.2f}s; chunks_ingested={chunks}")
    ok("Ingest E2E passed")


if __name__ == "__main__":
    main()
