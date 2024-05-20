import uvicorn
import logging
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from app.routes.user import UserRouter
from app.routes.candidate import CandidateRouter


app = FastAPI(title="Fast API", description="This is Code Graphers API's ")
app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(CandidateRouter, tags=["Candidate"], prefix="/candidate")

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger(__name__)
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

@app.get("/health", tags=["API Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)