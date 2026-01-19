"""Tests for filesystem service."""

import tempfile
from pathlib import Path

import pytest

from small_media.config import Settings
from small_media.services.filesystem import (
    get_folder_contents,
    is_safe_path,
    list_audio_files,
    list_folders,
)


@pytest.fixture
def temp_media_dir():
    """Create a temporary media directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create folder structure
        (base / "Album1").mkdir()
        (base / "Album1" / "track01.mp3").write_bytes(b"fake mp3")
        (base / "Album1" / "track02.wav").write_bytes(b"fake wav")

        (base / "Album2").mkdir()
        (base / "Album2" / "song.flac").write_bytes(b"fake flac")

        (base / "EmptyFolder").mkdir()

        (base / ".hidden").mkdir()
        (base / ".hidden" / "secret.mp3").write_bytes(b"hidden")

        yield base


@pytest.fixture
def settings(temp_media_dir):
    """Create settings for testing."""
    return Settings(
        media_path=temp_media_dir,
        cache_path=temp_media_dir / "cache",
        allowed_extensions="wav,mp3,flac",
    )


class TestIsSafePath:
    """Tests for is_safe_path function."""

    def test_safe_path(self, temp_media_dir):
        """Normal paths should be safe."""
        assert is_safe_path(temp_media_dir, "Album1")
        assert is_safe_path(temp_media_dir, "Album1/track01.mp3")

    def test_traversal_blocked(self, temp_media_dir):
        """Directory traversal should be blocked."""
        assert not is_safe_path(temp_media_dir, "../etc/passwd")
        assert not is_safe_path(temp_media_dir, "Album1/../../etc")


class TestListFolders:
    """Tests for list_folders function."""

    def test_lists_folders(self, temp_media_dir, settings):
        """Should list all non-hidden folders."""
        folders = list_folders(temp_media_dir, "", settings)

        names = [f.name for f in folders]
        assert "Album1" in names
        assert "Album2" in names
        assert "EmptyFolder" in names
        assert ".hidden" not in names

    def test_has_audio_flag(self, temp_media_dir, settings):
        """Should correctly identify folders with audio."""
        folders = list_folders(temp_media_dir, "", settings)
        folder_map = {f.name: f for f in folders}

        assert folder_map["Album1"].has_audio is True
        assert folder_map["Album2"].has_audio is True
        assert folder_map["EmptyFolder"].has_audio is False


class TestListAudioFiles:
    """Tests for list_audio_files function."""

    def test_lists_audio_files(self, temp_media_dir, settings):
        """Should list audio files in folder."""
        files = list_audio_files(temp_media_dir, "Album1", settings)

        filenames = [f.filename for f in files]
        assert "track01.mp3" in filenames
        assert "track02.wav" in filenames

    def test_file_format(self, temp_media_dir, settings):
        """Should correctly identify file format."""
        files = list_audio_files(temp_media_dir, "Album1", settings)
        file_map = {f.filename: f for f in files}

        assert file_map["track01.mp3"].format == "mp3"
        assert file_map["track02.wav"].format == "wav"


class TestGetFolderContents:
    """Tests for get_folder_contents function."""

    def test_gets_contents(self, temp_media_dir, settings):
        """Should get complete folder contents."""
        contents = get_folder_contents(temp_media_dir, "Album1", settings)

        assert contents is not None
        assert contents.name == "Album1"
        assert len(contents.files) == 2

    def test_nonexistent_folder(self, temp_media_dir, settings):
        """Should return None for nonexistent folder."""
        contents = get_folder_contents(temp_media_dir, "DoesNotExist", settings)
        assert contents is None
