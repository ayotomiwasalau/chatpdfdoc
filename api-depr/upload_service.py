import os
import aiofiles
from pipeline_service.pipeline import Pipeline
from fastapi import UploadFile, HTTPException
from llm_service.query import Query
from fastapi.responses import StreamingResponse
from app.schemas import QueryResponse
from db.log_data import LogData
from app.dependencies import ServiceDeps
class apiServices:
    def __init__(self, service_deps: ServiceDeps):
        self.chroma_db = service_deps.chroma_db
        self.llm = service_deps.llm
        self.config = service_deps.config
        self.log_data = service_deps.log_data

    def upload_via_url_svc(self, file_url: str):
        try:
            pipeline = Pipeline(filepath=file_url)
            run_id = pipeline.run()
            self.log_data.add_log(f"File uploaded to vector database: {run_id}")
            return run_id
        except Exception as e:
            self.log_data.add_log(f"Error in upload_via_url_svc: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def upload_via_ui_svc(self, file: UploadFile):
        path = f"/tmp/{file.filename}"
        try:
            # Stream to disk
            async with aiofiles.open(path, "wb") as out:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    await out.write(chunk)
            await file.close()

            pipeline = Pipeline(filepath=path)
            run_id = pipeline.run()

            self.log_data.add_log(f"File uploaded to vector database: {run_id}")
            os.remove(path)
            return run_id
        except Exception as e:
            self.log_data.add_log(f"Error in upload_via_ui_svc: {e}")
            raise HTTPException(status_code=400, detail=str(e))