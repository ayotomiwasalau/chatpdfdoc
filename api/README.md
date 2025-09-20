# RAG System API

FastAPI server for the RAG (Retrieval Augmented Generation) system with document upload and query capabilities.

## Prerequisites

Make sure you have:
1. Python 3.8+ installed
2. OpenAI API key set in your environment variables: `export OPENAI_API_KEY="your-api-key"`
3. All dependencies installed: `pip install -r ../requirement.txt`

## Running the Server

### Option 1: Using the run script
```bash
cd /Users/ayotomiwasalau/Documents/rag_system/api
python run_server.py
```

### Option 2: Using uvicorn directly
```bash
cd /Users/ayotomiwasalau/Documents/rag_system/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Endpoints

### 1. Health Check
- **GET** `/`
- Returns server status

### 2. Query Endpoint
- **POST** `/query`
- Query the LLM with RAG support

**Request Body:**
```json
{
  "query": "What experience does the candidate have with Python?"
}
```

**Response:**
```json
{
  "response": "Based on the context...",
  "status": "success"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What experience does the candidate have with Python?"}'
```

### 3. Upload Endpoint
- **POST** `/upload`
- Upload a PDF document via URL for processing

**Request Body:**
```json
{
  "file_url": "https://example.com/document.pdf"
}
```

**Response:**
```json
{
  "message": "Document processed successfully",
  "run_id": "uuid-string",
  "status": "success"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/resume.pdf"}'
```

## API Documentation

When the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Error Handling

The API includes comprehensive error handling:
- 400 Bad Request: Invalid input (empty query, non-PDF URL, etc.)
- 500 Internal Server Error: Processing errors

## CORS

CORS is enabled for all origins in development. For production, update the `allow_origins` in `main.py`.

## Notes

- Only PDF files are supported for upload
- The upload endpoint downloads the file temporarily, processes it through the pipeline, and then deletes the temporary file
- Query results are based on the documents previously uploaded and stored in the ChromaDB vector database
