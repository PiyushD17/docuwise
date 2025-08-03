from datetime import datetime

from pydantic import BaseModel


class FileMetadata(BaseModel):
    filename: str
    user_id: str
    upload_time: datetime
    file_path: str
    size: int
