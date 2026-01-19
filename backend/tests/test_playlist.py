"""Tests for playlist service."""

import tempfile
from pathlib import Path

import pytest
import yaml

from small_media.config import Settings
from small_media.services.playlist import (
    PLAYLIST_FILENAME,
    build_playlist,
    get_audio_files_in_folder,
    load_playlist_file,
    save_playlist_file,
    update_playlist,
)
from small_media.models import PlaylistTrackUpdate


@pytest.fixture
def temp_media_dir():
    """Create a temporary media directory with audio files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create folder with audio files
        album = base / "Album1"
        album.mkdir()
        (album / "track_03.mp3").write_bytes(b"fake mp3")
        (album / "track_01.mp3").write_bytes(b"fake mp3")
        (album / "track_02.mp3").write_bytes(b"fake mp3")

        yield base


@pytest.fixture
def settings(temp_media_dir):
    """Create settings for testing."""
    return Settings(
        media_path=temp_media_dir,
        cache_path=temp_media_dir / "cache",
        allowed_extensions="mp3,wav,flac",
    )


class TestGetAudioFiles:
    """Tests for get_audio_files_in_folder function."""

    def test_lists_audio_files(self, temp_media_dir, settings):
        """Should list audio files in folder."""
        files = get_audio_files_in_folder(temp_media_dir / "Album1", settings)
        assert len(files) == 3
        assert "track_01.mp3" in files
        assert "track_02.mp3" in files
        assert "track_03.mp3" in files

    def test_sorted_naturally(self, temp_media_dir, settings):
        """Files should be sorted naturally."""
        files = get_audio_files_in_folder(temp_media_dir / "Album1", settings)
        # Natural sort: 01, 02, 03
        assert files == ["track_01.mp3", "track_02.mp3", "track_03.mp3"]


class TestPlaylistFile:
    """Tests for playlist file operations."""

    def test_load_nonexistent(self, temp_media_dir):
        """Loading nonexistent playlist returns None."""
        data = load_playlist_file(temp_media_dir / "Album1")
        assert data is None

    def test_save_and_load(self, temp_media_dir):
        """Saving and loading playlist file works."""
        folder = temp_media_dir / "Album1"
        data = {
            "version": 1,
            "tracks": [
                {"filename": "track_02.mp3", "skip": False},
                {"filename": "track_01.mp3", "skip": True},
            ],
        }

        assert save_playlist_file(folder, data) is True

        loaded = load_playlist_file(folder)
        assert loaded is not None
        assert loaded["version"] == 1
        assert len(loaded["tracks"]) == 2


class TestBuildPlaylist:
    """Tests for build_playlist function."""

    def test_no_playlist_file(self, temp_media_dir, settings):
        """Without playlist file, tracks are in natural order."""
        tracks = build_playlist(temp_media_dir, "Album1", settings)
        assert len(tracks) == 3
        assert tracks[0].filename == "track_01.mp3"
        assert tracks[1].filename == "track_02.mp3"
        assert tracks[2].filename == "track_03.mp3"
        assert all(not t.skip for t in tracks)

    def test_with_playlist_file(self, temp_media_dir, settings):
        """With playlist file, tracks follow specified order."""
        folder = temp_media_dir / "Album1"
        data = {
            "version": 1,
            "tracks": [
                {"filename": "track_03.mp3", "skip": False},
                {"filename": "track_01.mp3", "skip": True},
            ],
        }
        save_playlist_file(folder, data)

        tracks = build_playlist(temp_media_dir, "Album1", settings)

        # First two are from playlist, third is remaining file
        assert tracks[0].filename == "track_03.mp3"
        assert tracks[0].skip is False
        assert tracks[1].filename == "track_01.mp3"
        assert tracks[1].skip is True
        assert tracks[2].filename == "track_02.mp3"
        assert tracks[2].skip is False


class TestUpdatePlaylist:
    """Tests for update_playlist function."""

    def test_update_creates_file(self, temp_media_dir, settings):
        """Updating playlist creates the playlist file."""
        folder = temp_media_dir / "Album1"
        playlist_path = folder / PLAYLIST_FILENAME

        assert not playlist_path.exists()

        updates = [
            PlaylistTrackUpdate(filename="track_02.mp3", skip=False),
            PlaylistTrackUpdate(filename="track_01.mp3", skip=True),
        ]
        tracks = update_playlist(temp_media_dir, "Album1", updates, settings)

        assert playlist_path.exists()
        assert tracks is not None
        assert tracks[0].filename == "track_02.mp3"
        assert tracks[1].filename == "track_01.mp3"
        assert tracks[1].skip is True

    def test_update_invalid_folder(self, temp_media_dir, settings):
        """Updating nonexistent folder returns None."""
        updates = [PlaylistTrackUpdate(filename="test.mp3", skip=False)]
        result = update_playlist(temp_media_dir, "DoesNotExist", updates, settings)
        assert result is None
