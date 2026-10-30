"""
FastAPI application entry point for Bangla Akinator Backend.
Lifespan management, strict CORS configuration, global error handlers, and route definitions.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import get_database, init_db_indexes, check_db_ready, close_database_connection
from app.core.logging_config import logger
from app.core.errors import AppException, ErrorResponse
from app.api.router import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle manager."""
    logger.info("Initializing Bangla Akinator FastAPI Service...")
    db = get_database()
    # Ensure indexes and uniqueness constraints on startup
    try:
        await init_db_indexes(db)
        logger.info("Database connection and indexes verified successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database indexes: {e}")

    yield

    logger.info("Shutting down Bangla Akinator Service...")
    await close_database_connection()


app = FastAPI(
    title="বাংলা জ্বিন API (Bangla Akinator)",
    description="Bayesian probability and Shannon entropy-powered guessing game backend for Bengali personalities.",
    version="2.0.0",
    lifespan=lifespan,
)

# Explicit origin CORS policy per adversarial review requirements
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Custom exception handler returning structured ErrorResponse."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            message_bn=exc.message_bn,
            details=exc.details,
        ).model_dump()
    )


# Mount API router
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe: verifies process is alive without leaking internal credentials."""
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe: validates MongoDB connectivity."""
    db = get_database()
    is_ready = await check_db_ready(db)
    if is_ready:
        return {"status": "ready", "database": "connected"}
    return JSONResponse(
        status_code=503,
        content={"status": "unhealthy", "database": "disconnected"}
    )
