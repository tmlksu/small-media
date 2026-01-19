"""Audio transcoding service using FFmpeg."""

import asyncio
import hashlib
import subprocess
from pathlib import Path
from typing import AsyncIterator

from ..config import Settings


def get_cache_key(file_path: Path, settings: Settings) -> str:
    """Generate a cache key based on file path, mtime, and output settings."""
    stat = file_path.stat()
    key_data = f"{file_path}:{stat.st_mtime}:{settings.audio_quality}:{settings.audio_bitrate}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def get_cached_path(file_path: Path, settings: Settings) -> Path:
    """Get the path where the cached transcoded file would be stored."""
    cache_key = get_cache_key(file_path, settings)
    return settings.cache_path / f"{cache_key}.mp3"


def is_mp3_passthrough(file_path: Path) -> bool:
    """Check if the file is an MP3 that can be passed through without transcoding."""
    return file_path.suffix.lower() == ".mp3"


def get_audio_duration(file_path: Path) -> float | None:
    """Get audio duration using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass
    return None


def get_audio_info(file_path: Path) -> dict:
    """Get audio metadata using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration,bit_rate:stream=sample_rate,channels",
                "-of", "json",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            format_info = data.get("format", {})
            stream_info = data.get("streams", [{}])[0] if data.get("streams") else {}
            
            return {
                "duration": float(format_info.get("duration", 0)),
                "bitrate": int(format_info.get("bit_rate", 0)) // 1000 if format_info.get("bit_rate") else None,
                "sample_rate": int(stream_info.get("sample_rate", 0)) if stream_info.get("sample_rate") else None,
                "channels": stream_info.get("channels"),
            }
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass
    return {"duration": 0, "bitrate": None, "sample_rate": None, "channels": None}


def transcode_to_cache(file_path: Path, cache_path: Path, settings: Settings) -> bool:
    """Transcode a file to MP3 and save to cache."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use VBR by default, fall back to CBR
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i", str(file_path),
        "-vn",  # No video
        "-codec:a", "libmp3lame",
        "-q:a", str(settings.audio_quality),  # VBR quality
        str(cache_path),
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=300,  # 5 minute timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        # Clean up partial file
        if cache_path.exists():
            cache_path.unlink()
        return False


async def stream_file(file_path: Path) -> AsyncIterator[bytes]:
    """Stream a file in chunks."""
    chunk_size = 64 * 1024  # 64KB chunks
    
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk
            # Allow other tasks to run
            await asyncio.sleep(0)


async def stream_transcoded(file_path: Path, settings: Settings) -> AsyncIterator[bytes]:
    """Stream a transcoded audio file.
    
    If cached, stream from cache. Otherwise, transcode on-the-fly and cache.
    """
    cached_path = get_cached_path(file_path, settings)
    
    # Check if already cached
    if cached_path.exists():
        async for chunk in stream_file(cached_path):
            yield chunk
        return
    
    # Check if MP3 passthrough
    if is_mp3_passthrough(file_path):
        async for chunk in stream_file(file_path):
            yield chunk
        return
    
    # Transcode to cache first, then stream
    # This is simpler than streaming while transcoding
    success = await asyncio.get_event_loop().run_in_executor(
        None, transcode_to_cache, file_path, cached_path, settings
    )
    
    if success and cached_path.exists():
        async for chunk in stream_file(cached_path):
            yield chunk
    else:
        # Fallback: stream original if transcoding failed
        async for chunk in stream_file(file_path):
            yield chunk


def ensure_cache_dir(settings: Settings) -> None:
    """Ensure cache directory exists."""
    settings.cache_path.mkdir(parents=True, exist_ok=True)


def get_cache_size(settings: Settings) -> int:
    """Get total size of cached files in bytes."""
    if not settings.cache_path.exists():
        return 0
    return sum(f.stat().st_size for f in settings.cache_path.glob("*.mp3"))


def clear_cache(settings: Settings) -> int:
    """Clear all cached files. Returns number of files deleted."""
    if not settings.cache_path.exists():
        return 0
    
    count = 0
    for f in settings.cache_path.glob("*.mp3"):
        f.unlink()
        count += 1
    return count
