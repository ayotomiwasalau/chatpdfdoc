from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import sys
import os
import tempfile
import requests
from urllib.parse import urlparse

# Add parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_service.query import Query
from pipeline_service.pipeline import Pipeline

# Initialize FastAPI app
app = FastAPI(
    title="RAG System API",
    description="API for querying LLM with RAG and uploading documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Query service
query_service = Query()

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What experience does the candidate have with Python?"
            }
        }

class QueryResponse(BaseModel):
    response: str
    status: str = "success"

class UploadRequest(BaseModel):
    file_url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_url": "https://example.com/document.pdf"
            }
        }

class UploadResponse(BaseModel):
    message: str
    run_id: Optional[str] = None
    status: str

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "RAG System API is running", "status": "healthy"}

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_llm(request: QueryRequest):
    """
    Query the LLM with RAG support.
    
    This endpoint accepts a query string and returns a response from the LLM
    based on the context from the vector database.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Use the Query service to get response
        response = query_service.query(request.query)
        
        return QueryResponse(
            response=response,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Upload endpoint
@app.post("/upload", response_model=UploadResponse)
async def upload_document(request: UploadRequest, background_tasks: BackgroundTasks):
    """
    Upload a document via URL for processing.
    
    This endpoint accepts a file URL, downloads the file, and processes it
    through the pipeline to store embeddings in the vector database.
    """
    try:
        # Validate URL
        file_url = str(request.file_url)
        parsed_url = urlparse(file_url)
        
        # Check if URL points to a PDF file
        if not parsed_url.path.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported. URL must end with .pdf"
            )
        
        # Download file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            response = requests.get(file_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Write content to temporary file
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            
            tmp_file_path = tmp_file.name
        
        # Process the file through the pipeline
        pipeline = Pipeline(tmp_file_path)
        run_id = pipeline.run()
        
        # Clean up temporary file after processing
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        
        return UploadResponse(
            message="Document processed successfully",
            run_id=run_id,
            status="success"
        )
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error downloading file from URL: {str(e)}"
        )
    except Exception as e:
        # Clean up temporary file on error
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing document: {str(e)}"
        )

# Run the application (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
