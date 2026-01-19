"""API routes for folder navigation."""

from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..models import ErrorResponse, FolderContents, FolderListResponse
from ..services.filesystem import get_folder_contents, is_safe_path, list_folders

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.get(
    "",
    response_model=FolderListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def list_root_folders() -> FolderListResponse:
    """List folders in the media root directory."""
    settings = get_settings()
    folders = list_folders(settings.media_path, "", settings)
    return FolderListResponse(folders=folders)


@router.get(
    "/{path:path}",
    response_model=FolderContents,
    responses={404: {"model": ErrorResponse}},
)
async def get_folder(path: str) -> FolderContents:
    """Get contents of a specific folder."""
    settings = get_settings()

    if not is_safe_path(settings.media_path, path):
        raise HTTPException(status_code=404, detail="Folder not found")

    contents = get_folder_contents(settings.media_path, path, settings)
    if contents is None:
        raise HTTPException(status_code=404, detail="Folder not found")

    return contents
