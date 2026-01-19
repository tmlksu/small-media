"""API routes for audio streaming."""

import urllib.parse
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..config import get_settings
from ..models import AudioInfo, ErrorResponse
from ..services.filesystem import decode_path, get_file_extension, is_safe_path
from ..services.transcoder import (
    get_audio_info,
    is_mp3_passthrough,
    stream_transcoded,
)

router = APIRouter(prefix="/stream", tags=["Stream"])


def get_content_type(file_path: Path, is_passthrough: bool) -> str:
    """Get MIME type for the audio response."""
    if is_passthrough:
        ext = file_path.suffix.lower()
        mime_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".flac": "audio/flac",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".mp4": "audio/mp4",
        }
        return mime_types.get(ext, "audio/mpeg")
    # Transcoded output is always MP3
    return "audio/mpeg"


@router.get(
    "/{path:path}",
    responses={404: {"model": ErrorResponse}},
)
async def stream_audio(path: str):
    """Stream audio file, transcoding if necessary."""
    settings = get_settings()

    # Validate path
    if not is_safe_path(settings.media_path, path):
        raise HTTPException(status_code=404, detail="File not found")

    # Resolve full path
    decoded_path = decode_path(path)
    file_path = settings.media_path / decoded_path

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Check if file extension is allowed
    ext = get_file_extension(file_path.name)
    if ext not in settings.allowed_extensions_set:
        raise HTTPException(status_code=404, detail="File type not supported")

    # Determine if passthrough
    is_passthrough = is_mp3_passthrough(file_path)
    content_type = get_content_type(file_path, is_passthrough)

    # Stream the audio
    return StreamingResponse(
        stream_transcoded(file_path, settings),
        media_type=content_type,
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        },
    )


@router.get(
    "/{path:path}/info",
    response_model=AudioInfo,
    responses={404: {"model": ErrorResponse}},
)
async def get_audio_metadata(path: str) -> AudioInfo:
    """Get metadata for an audio file."""
    settings = get_settings()

    # Validate path
    if not is_safe_path(settings.media_path, path):
        raise HTTPException(status_code=404, detail="File not found")

    # Resolve full path
    decoded_path = decode_path(path)
    file_path = settings.media_path / decoded_path

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Get audio info
    info = get_audio_info(file_path)
    
    return AudioInfo(
        filename=file_path.name,
        duration=info["duration"],
        format=get_file_extension(file_path.name),
        bitrate=info["bitrate"],
        sample_rate=info["sample_rate"],
        channels=info["channels"],
    )
