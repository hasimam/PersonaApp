"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import test, results, admin

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Personality matching app API - Find your idol twin!",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    test.router,
    prefix=f"{settings.API_V1_PREFIX}/test",
    tags=["test"]
)
app.include_router(
    results.router,
    prefix=f"{settings.API_V1_PREFIX}/results",
    tags=["results"]
)
app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["admin"]
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "PersonaApp API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check for monitoring."""
    return {"status": "healthy"}
