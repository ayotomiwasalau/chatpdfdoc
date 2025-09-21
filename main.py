import uvicorn
from app.controllers import app

if __name__ == "__main__":
    # Run the server with auto-reload for development
    uvicorn.run(
        "app.controllers:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )