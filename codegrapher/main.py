from fastapi import FastAPI, Request
from codegrapher.app.routes.user import UserRouter
from codegrapher.app.routes.candidate import CandidateRouter
from starlette.middleware.base import BaseHTTPMiddleware
from codegrapher.middleware import log_middleware, custom_exception_handler
from .app.database import test_connection
import sentry_sdk
import uvicorn

sentry_sdk.init(
    dsn="https://97c681481521e0fb4e21cf936b947be7@o4507296032358400.ingest.us.sentry.io/4507296035438592",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=0.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = FastAPI(title="Fast API", description="This is Code Graphers API's ")
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return custom_exception_handler(request, exc)

@app.on_event("startup")
async def startup_event():
    await test_connection()
    

app.include_router(UserRouter, tags=["User"])
app.include_router(CandidateRouter, tags=["Candidate"], prefix="/candidate")

    

@app.get("/health", tags=["API Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)