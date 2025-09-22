from typing import List
from fastapi import HTTPException
from pipeline_service.pipeline import Pipeline
from db.log_db import LogData

class DeleteService:
    def __init__(self, pipeline: Pipeline, log_data: LogData):
        self.pipeline = pipeline
        self.log_data = log_data

    def delete_svc(self, run_ids: List[str]):
        # Validate input early to provide consistent API errors
        if not run_ids or any((rid is None) or (not str(rid).strip()) for rid in run_ids):
            raise HTTPException(status_code=422, detail="run_ids must be a non-empty list of non-empty strings")

        try:
            self.pipeline.delete_documents(run_ids)
        except Exception as e:
            self.log_data.add_log(f"Failed to delete documents for run ids: {run_ids}", "error")
            raise HTTPException(status_code=500, detail=f"Failed to delete documents for run ids: {run_ids}") from e
        self.log_data.add_log(f"Deleted documents for run ids: {run_ids}", "info")