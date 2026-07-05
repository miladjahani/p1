"""
Heap Master Pro - Professional Metallurgical Engineering Platform
Main FastAPI Application with Modern Architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

from app.core.config import get_settings
from app.api.calculations import router as calculations_router
from app.api.pads import router as pads_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events"""
    settings = get_settings()
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Debug mode: {settings.DEBUG}")
    print(f"🌐 API Docs: http://localhost:8000/docs")
    yield
    print(f"👋 Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Application factory for creating FastAPI instance"""
    
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(calculations_router, prefix=settings.API_PREFIX)
    app.include_router(pads_router, prefix=settings.API_PREFIX)
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "timestamp": "2025-01-01T00:00:00Z"
        }
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "calculations": f"{settings.API_PREFIX}/calculate",
                "pads": f"{settings.API_PREFIX}/pads"
            }
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
