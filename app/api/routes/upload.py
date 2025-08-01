from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"application/pdf"}  # Add DOCX if needed


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
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
    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "original_filename": file.filename,
        "saved_as": new_filename,
        "saved_path": str(file_path),
        "size_kb": round(file_path.stat().st_size / 1024, 2),
        "timestamp": timestamp,
    }
