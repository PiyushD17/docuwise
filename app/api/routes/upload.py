import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.file_metadata import FileUploadResponse
from app.services.mongo_client import save_metadata

load_dotenv()

STORAGE_MODE = os.getenv("STORAGE_MODE")

router = APIRouter()
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"application/pdf"}  # Add DOCX if needed


@router.post("/upload", response_model=FileUploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> FileUploadResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, detail="Only PDF files are allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, detail="File too large (limit 10 MB)")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create a new filename with timestamp
    if not file.filename:
        raise HTTPException(400, detail="Filename is missing")

    original_name = Path(file.filename).stem
    extension = Path(file.filename).suffix
    new_filename = f"{original_name}_{timestamp}{extension}"

    file_path = UPLOAD_DIR / new_filename
    print(f"[UPLOAD] Writing to: {file_path.resolve()}")
    with open(file_path, "wb") as f:
        f.write(contents)

    metadata = {
        "original_filename": file.filename,
        "saved_as": new_filename,
        "saved_path": str(file_path),
        "size_kb": round(file_path.stat().st_size / 1024, 2),
        "timestamp": timestamp,
    }
    metadata["storage"] = STORAGE_MODE
    _ = save_metadata(metadata)

    return FileUploadResponse(**metadata)
