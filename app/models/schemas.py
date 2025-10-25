from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile
from typing import List


class QueryRequest(BaseModel):
    query: str
    run_ids: List[str] = []

class QueryResponse(BaseModel):
    answer: str


class UploadRequest(BaseModel):
    file: UploadFile


class UploadResponse(BaseModel):
    run_id: Optional[str] = None
    message: str = "success"

class DeleteRequest(BaseModel):
    run_ids: List[str]

class DeleteResponse(BaseModel):
    run_ids: List[str]
    message: str = "success"