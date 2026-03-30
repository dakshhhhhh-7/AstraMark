"""
Run server without reload to avoid subprocess issues
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server_enhanced:app",
        host="127.0.0.1",
        port=8001,
        reload=False,  # Disable reload to avoid subprocess
        log_level="info"
    )
