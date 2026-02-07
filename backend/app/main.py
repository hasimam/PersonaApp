"""
FastAPI application entry point.
"""

from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from app.core.config import settings
from app.api import admin, journey, results, test

# Docs configuration
DOCS_ENABLED = settings.ENVIRONMENT != "production"


def _require_admin_key(
    x_admin_key: Optional[str] = Header(None),
    admin_key: Optional[str] = Query(None),
) -> str:
    expected = settings.ADMIN_API_KEY
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY not configured")
    candidate = x_admin_key or admin_key
    if candidate != expected:
        raise HTTPException(status_code=401, detail="Invalid admin API key")
    return candidate


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Personality matching app API - Find your idol twin!",
    docs_url="/docs" if DOCS_ENABLED else None,
    redoc_url="/redoc" if DOCS_ENABLED else None,
    openapi_url="/openapi.json" if DOCS_ENABLED else None,
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
app.include_router(
    journey.router,
    prefix=f"{settings.API_V1_PREFIX}/journey",
    tags=["journey"]
)

if not DOCS_ENABLED:
    @app.get("/openapi.json", include_in_schema=False)
    def openapi_json(_: str = Depends(_require_admin_key)):
        return app.openapi()

    @app.get("/docs", include_in_schema=False)
    def swagger_ui(admin_key: str = Depends(_require_admin_key)):
        openapi_url = f"/openapi.json?admin_key={admin_key}"
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=f"{settings.PROJECT_NAME} - Docs",
        )

    @app.get("/redoc", include_in_schema=False)
    def redoc_ui(admin_key: str = Depends(_require_admin_key)):
        openapi_url = f"/openapi.json?admin_key={admin_key}"
        return get_redoc_html(
            openapi_url=openapi_url,
            title=f"{settings.PROJECT_NAME} - ReDoc",
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
