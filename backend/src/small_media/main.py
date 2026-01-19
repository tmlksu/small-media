"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import folders_router, playlist_router, stream_router
from .services.transcoder import ensure_cache_dir

app = FastAPI(
    title="Small Media API",
    description="Self-hosted private media player API",
    version="0.1.0",
)

# CORS middleware for frontend (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(folders_router, prefix="/api")
app.include_router(playlist_router, prefix="/api")
app.include_router(stream_router, prefix="/api")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    settings = get_settings()
    
    # Ensure cache directory exists
    ensure_cache_dir(settings)
    
    if settings.debug:
        print(f"Media path: {settings.media_path}")
        print(f"Cache path: {settings.cache_path}")
        print(f"Allowed extensions: {settings.allowed_extensions_set}")
    
    # Mount static files if frontend build exists (production mode)
    # Check multiple possible locations for the frontend dist
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "frontend" / "dist",  # Development
        Path("/app/frontend/dist"),  # Docker
    ]
    
    for frontend_dist in possible_paths:
        if frontend_dist.exists() and (frontend_dist / "index.html").exists():
            # Mount static files at root, with html=True for SPA routing
            app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
            if settings.debug:
                print(f"Serving static files from: {frontend_dist}")
            break
