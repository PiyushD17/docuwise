# app/api/routes/files_list.py
import ntpath
import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pymongo import DESCENDING, MongoClient

# --- Mongo setup ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/docuwise")
DB_NAME = os.getenv("MONGO_DB", "docuwise")
COLLECTION = os.getenv("MONGO_FILE_COLLECTION", "file_metadata")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db[COLLECTION]

# Helpful index (newest first if/when you add a real datetime field)
coll.create_index(
    [("timestamp", DESCENDING)], name="idx_timestamp_desc", background=True
)


# --- Pydantic models ---
class FileItem(BaseModel):
    id: str
    filename: str
    size: Optional[int] = None  # bytes
    uploaded_at: Optional[datetime] = None
    status: Optional[str] = None


class FileList(BaseModel):
    items: List[FileItem]


class FileStatus(BaseModel):
    id: str
    status: str


router = APIRouter()


def _pick_filename(d: dict, default_id: str) -> str:
    # prefer human name, then saved_as, then basename(saved_path)
    candidates = [
        # d.get("original_filename"),
        d.get("saved_as"),
    ]
    saved_path = d.get("saved_path")
    if isinstance(saved_path, str) and saved_path:
        candidates.append(ntpath.basename(saved_path))

    for c in candidates:
        if isinstance(c, str) and c.strip():
            return c.strip()

    return default_id


def _size_bytes(d: dict) -> Optional[int]:
    kb = d.get("size_kb")
    try:
        # Some ORMs store as string; handle both float and str
        if kb is None:
            return None
        if isinstance(kb, str):
            kb = float(kb)
        return int(round(kb * 1024))
    except Exception:
        return None


def _parse_timestamp(d: dict) -> Optional[datetime]:
    """
    Your format is "YYYYMMDD_HHMMSS" (e.g., 20250815_154321).
    """
    ts = d.get("timestamp")
    if not isinstance(ts, str):
        return None
    try:
        return datetime.strptime(ts, "%Y%m%d_%H%M%S")
    except Exception:
        return None


# GET /api/files?limit=10
@router.get("/files", response_model=FileList)
def list_files(limit: int = Query(10, ge=1, le=100)) -> dict:
    try:
        docs = (
            coll.find(
                {},
                projection={
                    "_id": 1,
                    "original_filename": 1,
                    "saved_as": 1,
                    "saved_path": 1,
                    "size_kb": 1,
                    "timestamp": 1,
                    "status": 1,
                },
            )
            .sort("timestamp", DESCENDING)  # matches your stored field
            .limit(limit)
        )

        items: List[FileItem] = []
        for d in docs:
            _id = d.get("_id")
            sid = str(_id) if _id is not None else ""
            items.append(
                FileItem(
                    id=sid,
                    filename=_pick_filename(d, sid),
                    size=_size_bytes(d),
                    uploaded_at=_parse_timestamp(d),
                    status=d.get("status") or "done",
                )
            )
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")


# Optional: GET /api/files/{file_id}/status
@router.get("/files/{file_id}/status", response_model=FileStatus)
def file_status(file_id: str) -> dict:
    try:
        oid = ObjectId(file_id) if ObjectId.is_valid(file_id) else file_id
        doc = coll.find_one({"_id": oid}, projection={"_id": 1, "status": 1})
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")
        return {"id": str(doc["_id"]), "status": doc.get("status", "done")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
