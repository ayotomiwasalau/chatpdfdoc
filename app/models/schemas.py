from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile


class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str


class UploadRequest(BaseModel):
    file: UploadFile


class UploadResponse(BaseModel):
    run_id: Optional[str] = None
    message: str = "success"
