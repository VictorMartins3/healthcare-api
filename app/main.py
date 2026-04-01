import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from app.api.routes import patients, notes, summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Healthcare API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(notes.router, tags=["notes"])  
app.include_router(summary.router, tags=["summary"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Healthcare API is running"}
