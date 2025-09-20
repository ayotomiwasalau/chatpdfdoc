#!/usr/bin/env python3
"""
Script to run the FastAPI server
"""
import uvicorn
from main import app

if __name__ == "__main__":
    # Run the server with auto-reload for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
