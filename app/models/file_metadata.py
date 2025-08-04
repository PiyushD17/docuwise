from typing import Literal

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    original_filename: str = Field(..., example="sample.pdf")
    saved_as: str = Field(..., example="sample_20250803_233323.pdf")
    saved_path: str = Field(..., example="data/sample_20250803_233323.pdf")
    size_kb: float = Field(..., example=342.82)
    timestamp: str = Field(..., example="20250803_233323")
    storage: Literal["local", "azure"] = Field(..., example="local")
