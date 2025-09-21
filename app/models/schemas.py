from pydantic import BaseModel, HttpUrl
from typing import Optional


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


class UploadRequest(BaseModel):
    file_url: HttpUrl


class UploadResponse(BaseModel):
    run_id: Optional[str] = None
    status: str = "success"
