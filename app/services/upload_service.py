import os
import aiofiles
from fastapi import UploadFile, HTTPException
from pipeline_service.pipeline import Pipeline
from db.log_db import LogData


class UploadService:
    def __init__(self, pipeline: Pipeline, log_data: LogData):
        self.pipeline = pipeline
        self.log_data = log_data

    async def upload_svc(self, file: UploadFile):
        if not file or not file.filename or not file.filename.strip():
            self.log_data.add_log(
                f"Upload failed - file name must not be empty")
            raise HTTPException(
                status_code=422, detail="File name must not be empty")

        if not file.content_type.startswith('application/pdf'):
            self.log_data.add_log(
                f"Upload failed - only PDF files are supported")
            raise HTTPException(
                status_code=422, detail="Only PDF files are supported")

        path = f"/tmp/{file.filename}"
        try:
            async with aiofiles.open(path, "wb") as out:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    await out.write(chunk)

            run_id = self.pipeline.run(filepath=path)
            self.log_data.add_log(
                f"File uploaded to vector database: {run_id}")
            return run_id
        except FileNotFoundError as e:
            self.log_data.add_log(f"Upload failed - file not found: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except ValueError as e:
            self.log_data.add_log(f"Upload failed - invalid input: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except RuntimeError as e:
            self.log_data.add_log(f"Upload failed - processing error: {e}")
            raise HTTPException(status_code=500, detail="Processing failed")
        except Exception as e:
            self.log_data.add_log(f"Unexpected error in upload_svc: {e}")
            raise HTTPException(
                status_code=500, detail="Internal server error")
        finally:
            await file.close()
            if os.path.exists(path):
                os.remove(path)
