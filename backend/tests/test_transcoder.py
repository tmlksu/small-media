"""Tests for transcoder service."""

import tempfile
from pathlib import Path

import pytest

from small_media.config import Settings
from small_media.services.transcoder import (
    get_cache_key,
    get_cached_path,
    is_mp3_passthrough,
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as media_dir:
        with tempfile.TemporaryDirectory() as cache_dir:
            yield Path(media_dir), Path(cache_dir)


@pytest.fixture
def settings(temp_dirs):
    """Create settings for testing."""
    media_dir, cache_dir = temp_dirs
    return Settings(
        media_path=media_dir,
        cache_path=cache_dir,
        audio_quality=2,
        audio_bitrate=192,
    )


class TestIsMp3Passthrough:
    """Tests for is_mp3_passthrough function."""

    def test_mp3_file(self, temp_dirs):
        """MP3 files should be passthrough."""
        media_dir, _ = temp_dirs
        mp3_file = media_dir / "test.mp3"
        mp3_file.write_bytes(b"fake mp3")
        assert is_mp3_passthrough(mp3_file) is True

    def test_wav_file(self, temp_dirs):
        """WAV files should not be passthrough."""
        media_dir, _ = temp_dirs
        wav_file = media_dir / "test.wav"
        wav_file.write_bytes(b"fake wav")
        assert is_mp3_passthrough(wav_file) is False

    def test_flac_file(self, temp_dirs):
        """FLAC files should not be passthrough."""
        media_dir, _ = temp_dirs
        flac_file = media_dir / "test.flac"
        flac_file.write_bytes(b"fake flac")
        assert is_mp3_passthrough(flac_file) is False


class TestCacheKey:
    """Tests for cache key generation."""

    def test_cache_key_format(self, temp_dirs, settings):
        """Cache key should be a hex string."""
        media_dir, _ = temp_dirs
        test_file = media_dir / "test.wav"
        test_file.write_bytes(b"test content")

        key = get_cache_key(test_file, settings)
        assert len(key) == 16
        assert all(c in "0123456789abcdef" for c in key)

    def test_different_files_different_keys(self, temp_dirs, settings):
        """Different files should produce different cache keys."""
        media_dir, _ = temp_dirs

        file1 = media_dir / "test1.wav"
        file1.write_bytes(b"content 1")

        file2 = media_dir / "test2.wav"
        file2.write_bytes(b"content 2")

        key1 = get_cache_key(file1, settings)
        key2 = get_cache_key(file2, settings)

        assert key1 != key2


class TestCachedPath:
    """Tests for cached path generation."""

    def test_cached_path_in_cache_dir(self, temp_dirs, settings):
        """Cached file should be in cache directory."""
        media_dir, cache_dir = temp_dirs
        test_file = media_dir / "test.wav"
        test_file.write_bytes(b"test content")

        cached = get_cached_path(test_file, settings)
        assert cached.parent == cache_dir

    def test_cached_path_is_mp3(self, temp_dirs, settings):
        """Cached file should have .mp3 extension."""
        media_dir, _ = temp_dirs
        test_file = media_dir / "test.flac"
        test_file.write_bytes(b"test content")

        cached = get_cached_path(test_file, settings)
        assert cached.suffix == ".mp3"
