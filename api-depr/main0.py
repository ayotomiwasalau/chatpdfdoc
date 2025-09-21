from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
import tempfile
import requests

# Import existing services
from llm_service.query import Query as LLMQuery
from pipeline_service.pipeline import Pipeline


app = FastAPI(title="RAG System API", version="1.0.0")


class QueryRequest(BaseModel):
    query: str


class UploadRequest(BaseModel):
    file_url: HttpUrl


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/query")
def query_endpoint(payload: QueryRequest):
    try:
        llm = LLMQuery()
        answer = llm.query(payload.query)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _download_to_tempfile(url: str) -> str:
    """Download a file from URL to a temp file and return the file path."""
    response = requests.get(url, stream=True, timeout=60)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to download file: {response.status_code}")

    # Infer extension from URL if present; default to .pdf for pipeline expectations
    _, ext = os.path.splitext(url)
    ext = ext if ext else ".pdf"

    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
        return tmp_path
    except Exception:
        # Ensure file is removed on failure
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


@app.post("/upload")
def upload_endpoint(payload: UploadRequest):
    try:
        tmp_path = _download_to_tempfile(str(payload.file_url))
        try:
            pipeline = Pipeline(filepath=tmp_path)
            run_id = pipeline.run()
            return {"run_id": run_id}
        finally:
            # Clean up the temporary file after pipeline processes it
            try:
                os.remove(tmp_path)
            except Exception:
                # Best-effort cleanup; ignore errors
                pass
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


