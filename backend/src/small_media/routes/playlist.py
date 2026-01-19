"""API routes for playlist management."""

from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..models import ErrorResponse, Playlist, PlaylistUpdate
from ..services.filesystem import decode_path, is_safe_path
from ..services.playlist import build_playlist, update_playlist

router = APIRouter(tags=["Playlist"])


@router.get(
    "/folders/{path:path}/playlist",
    response_model=Playlist,
    responses={404: {"model": ErrorResponse}},
)
async def get_playlist(path: str) -> Playlist:
    """Get playlist for a folder with ordered tracks and skip flags."""
    settings = get_settings()

    # Validate path
    if path and not is_safe_path(settings.media_path, path):
        raise HTTPException(status_code=404, detail="Folder not found")

    # Check folder exists
    if path:
        folder_path = settings.media_path / decode_path(path)
    else:
        folder_path = settings.media_path

    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    tracks = build_playlist(settings.media_path, path, settings)

    return Playlist(path=path, tracks=tracks)


@router.put(
    "/folders/{path:path}/playlist",
    response_model=Playlist,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def update_folder_playlist(path: str, data: PlaylistUpdate) -> Playlist:
    """Update playlist order and skip flags for a folder."""
    settings = get_settings()

    # Validate path
    if path and not is_safe_path(settings.media_path, path):
        raise HTTPException(status_code=404, detail="Folder not found")

    # Update playlist
    tracks = update_playlist(settings.media_path, path, data.tracks, settings)

    if tracks is None:
        raise HTTPException(status_code=404, detail="Folder not found")

    return Playlist(path=path, tracks=tracks)
