from fastapi import Request
from starlette.responses import JSONResponse
import logging
import sys

logger = logging.getLogger()

formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]

logger.setLevel(logging.INFO)
async def log_middleware(request: Request, call_next):
    logger.info(f"Request log {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response log {response.status_code}")
    return response

async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )
