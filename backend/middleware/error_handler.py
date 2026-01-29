from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
import logging
import os

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if os.getenv("ENVIRONMENT") == "production":
        message = "An error occurred. Please try again later."
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": message,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

def add_exception_handlers(app: FastAPI):
    app.add_exception_handler(Exception, global_exception_handler)
