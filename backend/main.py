"""
Polyglot AI Studio
------------------

Main FastAPI Application
"""

import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as document_router
from app.api.export import router as export_router
from app.api.extraction import router as extraction_router
from app.api.matching import router as matching_router
from app.api.translation import router as translation_router
from app.api.upload import router as upload_router

# Database
from db.postgres import Base, create_database_if_not_exists, engine

# Register all SQLAlchemy models
from db import models


# ============================================================
# Rate limiter (shared across all routers via app.state)
# ============================================================

limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])


# ============================================================
# Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 70)
    print("Starting Polyglot AI Studio Backend")
    print("=" * 70)

    # Database
    print("Checking PostgreSQL database...")
    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
    print("Database ready.")

    # Dedicated thread pool for CPU-bound AI inference.
    # max_workers=2 lets two requests run model inference concurrently while
    # keeping memory use predictable (each extra worker loads ~700 MB of models).
    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ai-worker")
    app.state.executor = executor

    # Pre-load both models in the background thread so the first real request
    # doesn't pay the download/load cost.
    print("Pre-loading AI models (this may take a moment on first run)...")
    loop = __import__("asyncio").get_event_loop()
    from app.services.chat_service import get_chat_service

    def _warmup():
        svc = get_chat_service()
        svc._get_embed_model()
        svc._get_qa_pipeline()

    await loop.run_in_executor(executor, _warmup)
    print("AI models ready.")

    print("=" * 70)
    print("Backend ready.")
    print("=" * 70 + "\n")

    yield

    executor.shutdown(wait=False)
    print("\nShutting down Polyglot AI Studio...\n")


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Polyglot AI Studio API",
    description="Multilingual Document Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach the limiter so @limiter.limit decorators can find it
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================
# Middleware
# ============================================================

# Read from env so production deployments only need to set FRONTEND_URL
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routers
# ============================================================

app.include_router(auth_router,       prefix="/api/v1/auth",      tags=["Authentication"])
app.include_router(upload_router,     prefix="/api/v1/upload",    tags=["Document Intelligence"])
app.include_router(document_router,   prefix="/api/v1/documents", tags=["Documents"])
app.include_router(translation_router,prefix="/api/v1/translate", tags=["Translation"])
app.include_router(chat_router,       prefix="/api/v1/documents", tags=["Chat"])
app.include_router(extraction_router, prefix="/api/v1/documents", tags=["Extraction"])
app.include_router(matching_router,   prefix="/api/v1/documents", tags=["Matching"])
app.include_router(export_router,     prefix="/api/v1/documents", tags=["Export"])
app.include_router(export_router,     prefix="/api/v1",           tags=["Export"])


# ============================================================
# Root / Health
# ============================================================

@app.get("/", tags=["Root"])
def root():
    return {"application": "Polyglot AI Studio", "version": "1.0.0", "status": "Running"}


@app.get("/api/v1/health", tags=["Health"])
def health():
    return {"status": "healthy", "database": "connected"}
