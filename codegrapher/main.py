import uvicorn
from celery import Celery
from fastapi import FastAPI, Request
from codegrapher.app.routes.user import UserRouter
from codegrapher.app.routes.candidate import CandidateRouter
from starlette.middleware.base import BaseHTTPMiddleware
from codegrapher.middleware import log_middleware, custom_exception_handler


app = FastAPI(title="Fast API", description="This is Code Graphers API's ")
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6380/0",
    backend="redis://127.0.0.1:6380/0"
)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return custom_exception_handler(request, exc)

app.include_router(UserRouter, tags=["User"])
app.include_router(CandidateRouter, tags=["Candidate"], prefix="/candidate")


@app.get("/health", tags=["API Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}

@celery.task
def divide(x, y):
    import time
    time.sleep(5)
    return x / y


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)