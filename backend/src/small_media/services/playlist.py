"""Playlist management service."""

from pathlib import Path
from typing import Any

import yaml

from ..config import Settings
from ..models import PlaylistTrack, PlaylistTrackUpdate
from .filesystem import decode_path, encode_path, get_file_extension, is_audio_file

PLAYLIST_FILENAME = ".small-media-playlist.yaml"


def get_playlist_path(folder_path: Path) -> Path:
    """Get the path to the playlist file for a folder."""
    return folder_path / PLAYLIST_FILENAME


def load_playlist_file(folder_path: Path) -> dict[str, Any] | None:
    """Load playlist YAML file if it exists."""
    playlist_path = get_playlist_path(folder_path)
    if not playlist_path.exists():
        return None

    try:
        with open(playlist_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return data
    except (yaml.YAMLError, OSError):
        pass
    return None


def save_playlist_file(folder_path: Path, data: dict[str, Any]) -> bool:
    """Save playlist data to YAML file."""
    playlist_path = get_playlist_path(folder_path)
    try:
        with open(playlist_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return True
    except OSError:
        return False


def get_audio_files_in_folder(folder_path: Path, settings: Settings) -> list[str]:
    """Get list of audio filenames in a folder, sorted naturally."""
    if not folder_path.exists() or not folder_path.is_dir():
        return []

    files = []
    allowed_ext = settings.allowed_extensions_set

    for item in sorted(folder_path.iterdir(), key=lambda x: x.name.lower()):
        if item.is_file() and is_audio_file(item.name, allowed_ext):
            files.append(item.name)

    return files


def build_playlist(
    base_path: Path,
    relative_path: str,
    settings: Settings,
) -> list[PlaylistTrack]:
    """Build playlist for a folder.

    Tracks listed in the playlist file come first in specified order.
    Remaining tracks appear after in natural sort order.
    """
    if relative_path:
        folder_path = base_path / decode_path(relative_path)
    else:
        folder_path = base_path

    # Get all audio files in folder
    all_files = set(get_audio_files_in_folder(folder_path, settings))
    if not all_files:
        return []

    # Load playlist data
    playlist_data = load_playlist_file(folder_path)

    # Build ordered list
    tracks = []
    seen_files: set[str] = set()

    # Process files from playlist first
    if playlist_data and "tracks" in playlist_data:
        for track_data in playlist_data["tracks"]:
            if not isinstance(track_data, dict):
                continue

            filename = track_data.get("filename")
            if not filename or filename not in all_files:
                continue

            skip = bool(track_data.get("skip", False))
            rel_file_path = f"{relative_path}/{filename}" if relative_path else filename

            tracks.append(
                PlaylistTrack(
                    filename=filename,
                    path=encode_path(rel_file_path),
                    skip=skip,
                    duration=None,
                )
            )
            seen_files.add(filename)

    # Add remaining files not in playlist
    remaining = sorted(all_files - seen_files, key=str.lower)
    for filename in remaining:
        rel_file_path = f"{relative_path}/{filename}" if relative_path else filename
        tracks.append(
            PlaylistTrack(
                filename=filename,
                path=encode_path(rel_file_path),
                skip=False,
                duration=None,
            )
        )

    return tracks


def update_playlist(
    base_path: Path,
    relative_path: str,
    updates: list[PlaylistTrackUpdate],
    settings: Settings,
) -> list[PlaylistTrack] | None:
    """Update playlist order and skip flags.

    Returns the updated playlist or None if folder doesn't exist.
    """
    if relative_path:
        folder_path = base_path / decode_path(relative_path)
    else:
        folder_path = base_path

    if not folder_path.exists() or not folder_path.is_dir():
        return None

    # Validate that all files exist
    all_files = set(get_audio_files_in_folder(folder_path, settings))
    update_files = {u.filename for u in updates}

    # Only include files that actually exist
    valid_updates = [u for u in updates if u.filename in all_files]

    # Build playlist data
    playlist_data = {
        "version": 1,
        "tracks": [
            {"filename": u.filename, "skip": u.skip}
            for u in valid_updates
        ],
    }

    # Save to file
    if not save_playlist_file(folder_path, playlist_data):
        return None

    # Return updated playlist
    return build_playlist(base_path, relative_path, settings)
