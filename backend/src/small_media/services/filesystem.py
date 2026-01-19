"""File system operations for media library."""

import urllib.parse
from pathlib import Path

from ..config import Settings
from ..models import AudioFile, FolderContents, FolderItem


def is_safe_path(base_path: Path, requested_path: str) -> bool:
    """Check if the requested path is safe (no directory traversal)."""
    if ".." in requested_path:
        return False

    # Decode and resolve the full path
    decoded = urllib.parse.unquote(requested_path)
    full_path = (base_path / decoded).resolve()

    # Ensure it's still under the base path
    try:
        full_path.relative_to(base_path.resolve())
        return True
    except ValueError:
        return False


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension without the dot."""
    return Path(filename).suffix.lower().lstrip(".")


def is_audio_file(filename: str, allowed_extensions: set[str]) -> bool:
    """Check if a file is a supported audio file."""
    return get_file_extension(filename) in allowed_extensions


def encode_path(path: str) -> str:
    """URL-encode a path for use in API responses."""
    return urllib.parse.quote(path, safe="")


def decode_path(encoded_path: str) -> str:
    """Decode a URL-encoded path."""
    return urllib.parse.unquote(encoded_path)


def folder_has_audio(folder_path: Path, allowed_extensions: set[str]) -> bool:
    """Check if a folder contains any audio files (non-recursive)."""
    try:
        for item in folder_path.iterdir():
            if item.is_file() and is_audio_file(item.name, allowed_extensions):
                return True
    except PermissionError:
        pass
    return False


def count_subfolders(folder_path: Path) -> int:
    """Count immediate subfolders."""
    try:
        return sum(1 for item in folder_path.iterdir() if item.is_dir())
    except PermissionError:
        return 0


def list_folders(base_path: Path, relative_path: str, settings: Settings) -> list[FolderItem]:
    """List folders in a directory."""
    if relative_path:
        full_path = base_path / decode_path(relative_path)
    else:
        full_path = base_path

    if not full_path.exists() or not full_path.is_dir():
        return []

    folders = []
    allowed_ext = settings.allowed_extensions_set

    try:
        for item in sorted(full_path.iterdir(), key=lambda x: x.name.lower()):
            if item.is_dir() and not item.name.startswith("."):
                rel_path = str(item.relative_to(base_path))
                folders.append(
                    FolderItem(
                        name=item.name,
                        path=encode_path(rel_path),
                        has_audio=folder_has_audio(item, allowed_ext),
                        subfolder_count=count_subfolders(item),
                    )
                )
    except PermissionError:
        pass

    return folders


def list_audio_files(base_path: Path, relative_path: str, settings: Settings) -> list[AudioFile]:
    """List audio files in a directory."""
    if relative_path:
        full_path = base_path / decode_path(relative_path)
    else:
        full_path = base_path

    if not full_path.exists() or not full_path.is_dir():
        return []

    files = []
    allowed_ext = settings.allowed_extensions_set

    try:
        for item in sorted(full_path.iterdir(), key=lambda x: x.name.lower()):
            if item.is_file() and is_audio_file(item.name, allowed_ext):
                rel_path = str(item.relative_to(base_path))
                files.append(
                    AudioFile(
                        filename=item.name,
                        path=encode_path(rel_path),
                        format=get_file_extension(item.name),
                        size=item.stat().st_size,
                    )
                )
    except PermissionError:
        pass

    return files


def get_folder_contents(
    base_path: Path, relative_path: str, settings: Settings
) -> FolderContents | None:
    """Get complete folder contents."""
    if relative_path and not is_safe_path(base_path, relative_path):
        return None

    if relative_path:
        full_path = base_path / decode_path(relative_path)
        name = full_path.name
    else:
        full_path = base_path
        name = "Root"

    if not full_path.exists() or not full_path.is_dir():
        return None

    return FolderContents(
        path=relative_path,
        name=name,
        folders=list_folders(base_path, relative_path, settings),
        files=list_audio_files(base_path, relative_path, settings),
    )
