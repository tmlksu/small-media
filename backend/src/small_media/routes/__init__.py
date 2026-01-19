"""API routes package."""

from .folders import router as folders_router
from .playlist import router as playlist_router
from .stream import router as stream_router

__all__ = ["folders_router", "playlist_router", "stream_router"]

