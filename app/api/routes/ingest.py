from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.services.chunker import TextChunker
from app.services.embedder import TextEmbedder
from app.services.indexer import FAISSIndexer
from app.services.pdf_loader import PDFLoader

router = APIRouter()
UPLOAD_DIR = Path("data")


@router.post("/ingest")
async def ingest_file(
    filename: str = Query(..., description="Filename saved during upload"),
) -> dict:
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Step 1: Load PDF
    try:
        pdf_loader = PDFLoader(file_path)
        document_text: list[str] = pdf_loader.load_text(by_page=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PDF: {e}")

    # Step 2: Chunk
    try:
        chunker = TextChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(document_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error chunking text: {e}")

    # Step 3: Embed
    try:
        embedder = TextEmbedder()
        embeddings = embedder.embed(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {e}")

    # Step 4: Metadata & Indexing
    try:
        metadata = [{"filename": filename, "chunk_id": i} for i in range(len(chunks))]
        indexer = FAISSIndexer(dim=len(embeddings[0]))
        num_vectors, num_metadata = indexer.add_embeddings(embeddings, metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing embeddings: {e}")

    return {
        "filename": filename,
        "chunks_ingested": len(chunks),
        "message": "Ingestion successful",
    }
