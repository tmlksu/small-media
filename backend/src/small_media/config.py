"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    """Find .env file in current directory or parent directories."""
    current = Path.cwd()
    for _ in range(5):  # Search up to 5 levels
        env_file = current / ".env"
        if env_file.exists():
            return env_file
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required paths
    media_path: Path = Path("/media")
    cache_path: Path = Path("/cache")

    # Audio settings
    audio_quality: int = 2  # LAME VBR quality (0-9, lower = better)
    audio_bitrate: int = 192  # CBR fallback bitrate in kbps

    # Allowed extensions
    allowed_extensions: str = "wav,mp3,m4a,mp4,flac,ogg"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    @property
    def allowed_extensions_set(self) -> set[str]:
        """Get allowed extensions as a set."""
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",")}

    def validate_paths(self) -> None:
        """Validate that required paths exist."""
        if not self.media_path.exists():
            raise ValueError(f"MEDIA_PATH does not exist: {self.media_path}")
        if not self.cache_path.exists():
            # Try to create cache directory
            self.cache_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
