#!/usr/bin/env python
"""
DocuWise E2E Smoke Test (mypy-clean)

- GET /health
- Detect /api upload endpoint from OpenAPI (or fallbacks)
- Upload data/sample.pdf (multipart, Content-Type: application/pdf)
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import Any, Dict, List, Mapping, NoReturn, Optional, Tuple, cast

import requests

ROOT: str = os.getenv("ROOT_URL", "http://localhost:8000").rstrip("/")
API_PREFIX: str = os.getenv("API_PREFIX", "/api")
API: str = f"{ROOT}{API_PREFIX.rstrip('/')}"
SAMPLE_PATH: str = os.getenv("SAMPLE_PATH", "data/sample.pdf")

SAMPLE = pathlib.Path(SAMPLE_PATH)

# Common multipart field names to try if OpenAPI doesn't tell us
FALLBACK_FIELD_NAMES: List[str] = ["file", "upload", "document", "pdf", "data"]


def fail(msg: str, code: int = 1) -> NoReturn:
    print(f"❌ {msg}")
    sys.exit(code)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def probe_health() -> None:
    print("🔎 Checking API health at /health …")
    try:
        r: requests.Response = requests.get(f"{ROOT}/health", timeout=8)
    except Exception as e:  # pragma: no cover
        fail(f"Health request error: {e}")
    if not r.ok:
        fail(f"Health check failed: HTTP {r.status_code} {r.text}")
    try:
        body: Dict[str, Any] = cast(Dict[str, Any], r.json())
    except Exception:
        fail("Health response was not JSON")
    if body.get("status") != "ok":
        fail(f"Health JSON unexpected: {body}")
    ok("API healthy")


def fetch_openapi() -> Optional[Dict[str, Any]]:
    try:
        r: requests.Response = requests.get(f"{ROOT}/openapi.json", timeout=8)
        if r.ok:
            return cast(Dict[str, Any], r.json())
    except Exception:
        return None
    return None


def detect_upload_from_openapi(
    spec: Dict[str, Any],
) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (path, field_name) if a multipart/form-data POST endpoint is found.
    Prefer routes under API_PREFIX and with 'upload' in the path.
    If schema has properties, use the first property key as the field name.
    """
    paths: Mapping[str, Any] = cast(Mapping[str, Any], (spec or {}).get("paths", {}))
    matches: List[Tuple[str, Optional[str]]] = []

    for path, ops in paths.items():
        post = (cast(Dict[str, Any], ops) or {}).get("post")
        if not isinstance(post, dict):
            continue
        req_body: Dict[str, Any] = cast(Dict[str, Any], post.get("requestBody") or {})
        content: Dict[str, Any] = cast(Dict[str, Any], req_body.get("content") or {})

        # Look for multipart/form-data
        multipart_keys: List[str] = [
            ct
            for ct in content.keys()
            if isinstance(ct, str) and ct.lower().startswith("multipart/form-data")
        ]
        if not multipart_keys:
            continue

        # If there is a schema with properties, capture a likely field name
        field_name: Optional[str] = None
        try:
            schema = cast(
                Dict[str, Any], content[multipart_keys[0]].get("schema") or {}
            )
            props = cast(Dict[str, Any], schema.get("properties") or {})
            if props:
                field_name = next(iter(props.keys()))
        except Exception:
            pass

        matches.append((cast(str, path), field_name))

    if not matches:
        return (None, None)

    def score(item: Tuple[str, Optional[str]]) -> int:
        path, _ = item
        s = 0
        if path.startswith(API_PREFIX):
            s += 10
        if "upload" in path.lower():
            s += 5
        if "file" in path.lower() or "files" in path.lower():
            s += 2
        return s

    matches.sort(key=score, reverse=True)
    return matches[0]


def detect_upload_endpoint() -> Tuple[Optional[str], Optional[str]]:
    # 1) Try OpenAPI
    spec = fetch_openapi()
    if spec:
        path, field = detect_upload_from_openapi(spec)
        if path:
            return (path, field)

    # 2) Fallback candidates under /api
    candidates: List[str] = [
        "/upload",
        "/files/upload",
        "/upload/file",
        "/ingest",
        "/documents/upload",
    ]
    for c in candidates:
        candidate = f"{API_PREFIX.rstrip('/')}{c}"
        try:
            # OPTIONS is often allowed; 405 means path exists but method differs
            r: requests.Response = requests.options(f"{ROOT}{candidate}", timeout=5)
            if r.ok or r.status_code in (200, 204, 405):
                return (candidate, None)
        except Exception:
            continue

    return (None, None)


def ensure_sample_exists() -> None:
    if not SAMPLE.exists():
        fail(f"Sample PDF not found at {SAMPLE}. Please add a real PDF file there.")
    # Light validation: extension + magic bytes (non-fatal, just warn)
    try:
        with open(SAMPLE, "rb") as f:
            head = f.read(5)
        if not head.startswith(b"%PDF"):
            print(
                "⚠️  sample.pdf does not start with %PDF - if the server checks magic bytes, use a real PDF."
            )
    except Exception:
        print("⚠️  Unable to read sample.pdf for validation; continuing…")


def try_upload(path: str, field_name_hint: Optional[str]) -> Dict[str, Any]:
    url = f"{ROOT}{path}"
    fields_to_try: List[str] = []
    if field_name_hint:
        fields_to_try.append(field_name_hint)
    # extend with fallbacks (preserve order and uniqueness)
    fields_to_try += [n for n in FALLBACK_FIELD_NAMES if n not in fields_to_try]

    last_status: Optional[int] = None
    last_text: Optional[str] = None

    for field in fields_to_try:
        print(f"📤 Uploading sample.pdf to {url} with field '{field}' …")
        try:
            with open(SAMPLE, "rb") as f:
                files = {field: ("sample.pdf", f, "application/pdf")}
                r: requests.Response = requests.post(url, files=files, timeout=60)
        except Exception as e:
            last_status, last_text = None, str(e)
            print(f"   ↳ error: {e}")
            continue

        if r.ok:
            ok(f"Upload succeeded using field '{field}'")
            try:
                return cast(Dict[str, Any], r.json())
            except Exception:
                # If server returns non-JSON success
                return {"raw": r.text}

        # keep last failure info
        last_status, last_text = r.status_code, r.text
        print(f"   ↳ server responded {last_status}: {last_text[:200]}")

    fail(f"Upload failed for all tried fields. Last error: {last_status} {last_text}")


def main() -> None:
    print(f"ROOT: {ROOT}")
    print(f"API:  {API}")
    probe_health()
    ensure_sample_exists()

    path, field_hint = detect_upload_endpoint()
    if not path:
        fail(
            f"Could not detect an upload endpoint under {API_PREFIX}. "
            f"Open {ROOT}/docs and confirm the path.",
            code=2,
        )

    print(f"📍 Using upload endpoint: {path}")
    if field_hint:
        print(f"📌 Detected file field from OpenAPI: '{field_hint}'")

    meta: Dict[str, Any] = try_upload(path, field_hint)
    print("📄 Upload response:")
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    ok("E2E smoke passed")


if __name__ == "__main__":
    main()
