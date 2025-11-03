"""
Main FastAPI application for Scout Badge Inventory backend.

This module initializes the FastAPI application with CORS middleware,
health check endpoints, and API routes.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import APIConfig, DatabaseConfig, UploadConfig


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.

    Handles initialization and cleanup tasks for the application.
    """
    # Startup
    print("Starting Scout Badge Inventory API...")
    print(f"Database: {DatabaseConfig.URL}")
    print(f"Upload directory: {UploadConfig.UPLOAD_DIR}")

    # Ensure upload directory exists
    UploadConfig.ensure_upload_dir()

    yield

    # Shutdown
    print("Shutting down Scout Badge Inventory API...")


# Initialize FastAPI application
app = FastAPI(
    title=APIConfig.TITLE,
    description=APIConfig.DESCRIPTION,
    version=APIConfig.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=APIConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """
    Root endpoint returning API information.

    Returns:
        dict: Basic API information
    """
    return {
        "name": APIConfig.TITLE,
        "version": APIConfig.VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "database": "connected",
        "upload_dir": str(UploadConfig.UPLOAD_DIR),
    }


@app.get("/api/health", tags=["Health"])
async def api_health_check() -> dict[str, str]:
    """
    API health check endpoint.

    Returns:
        dict: API health status
    """
    return {
        "status": "healthy",
        "version": APIConfig.VERSION,
    }


# API router setup
from backend.api import upload_router

app.include_router(upload_router, prefix="/api", tags=["Upload"])


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc) -> JSONResponse:
    """Handle 404 Not Found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc) -> JSONResponse:
    """Handle 500 Internal Server errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        reload=APIConfig.RELOAD,
    )
