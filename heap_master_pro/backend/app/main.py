"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.routers import auth, pads, projects, users, reports


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Heap Master Pro API")
    
    # Initialize database (in production, use migrations)
    if settings.DEBUG:
        init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Heap Master Pro API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Heap Master Pro API

Professional industrial software for heap leach pad design and management.

### Features
- **Pad Management**: Create, update, and manage heap leach pads
- **Engineering Calculations**: Volume, tonnage, recoverable metal estimates
- **3D Visualization**: Three.js-based 3D rendering data
- **Irrigation Design**: Emitter spacing, flow rate calculations
- **Reports**: Generate PDF and Excel reports
- **Multi-Tenant**: Support for multiple companies and projects

### Authentication
All endpoints require authentication except `/api/v1/auth/login` and `/api/v1/auth/register`.
Use JWT tokens in the Authorization header: `Bearer <token>`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred",
            "type": type(exc).__name__,
        }
    )


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(pads.router, prefix="/api/v1/pads", tags=["Pads"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
