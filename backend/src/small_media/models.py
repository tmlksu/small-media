"""Pydantic models for API requests and responses."""

from pathlib import Path

from pydantic import BaseModel


class FolderItem(BaseModel):
    """A folder in the media library."""

    name: str
    path: str  # URL-encoded relative path
    has_audio: bool
    subfolder_count: int


class AudioFile(BaseModel):
    """An audio file in a folder."""

    filename: str
    path: str  # URL-encoded relative path for streaming
    format: str
    size: int  # File size in bytes


class FolderContents(BaseModel):
    """Contents of a folder."""

    path: str
    name: str
    folders: list[FolderItem]
    files: list[AudioFile]


class FolderListResponse(BaseModel):
    """Response for folder listing."""

    folders: list[FolderItem]


class PlaylistTrack(BaseModel):
    """A track in a playlist."""

    filename: str
    path: str
    skip: bool = False
    duration: float | None = None


class Playlist(BaseModel):
    """Playlist for a folder."""

    path: str
    tracks: list[PlaylistTrack]


class PlaylistTrackUpdate(BaseModel):
    """Track update for playlist."""

    filename: str
    skip: bool = False


class PlaylistUpdate(BaseModel):
    """Request to update playlist order."""

    tracks: list[PlaylistTrackUpdate]


class AudioInfo(BaseModel):
    """Audio file metadata."""

    filename: str
    duration: float
    format: str
    bitrate: int | None = None
    sample_rate: int | None = None
    channels: int | None = None


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    details: str | None = None
