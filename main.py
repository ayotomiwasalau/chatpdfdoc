import uvicorn
from app.controllers import app
import os

print("*************************************************************")
print("Check db/rag.txt for logs")
print("*************************************************************")

if __name__ == "__main__":
    # Run the server with auto-reload for development

    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run(
        "app.controllers:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
