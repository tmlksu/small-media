# Installation Guide

This guide covers setting up Small Media for development and production.

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 20+ (for frontend)
- **FFmpeg**: 6.0+ (for transcoding)
- **uv**: Python package manager
- **pnpm**: Node.js package manager (recommended)

## Quick Start

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### 2. Install uv (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Clone and Setup

```bash
git clone https://github.com/your-username/small-media.git
cd small-media

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend
pnpm install
cd ..
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
vim .env
```

Required environment variables:

```bash
# Path to media files (HDD)
MEDIA_PATH=/path/to/your/media

# Path for transcoded cache (SSD recommended)
CACHE_PATH=/path/to/cache

# Optional: Audio settings
AUDIO_QUALITY=2        # LAME VBR quality (0-9, lower = better)
AUDIO_BITRATE=192      # Fallback CBR bitrate
```

### 5. Run Development Servers

```bash
# Using poe tasks (recommended)
poe dev

# Or manually:
# Terminal 1: Backend
uv run uvicorn small_media.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && pnpm dev
```

Visit `http://localhost:5173` to access the application.

---

## Poe Tasks Reference

All common tasks are defined in `pyproject.toml`:

| Task | Command | Description |
|------|---------|-------------|
| `poe dev` | Start development servers | Backend + Frontend |
| `poe backend` | Start backend only | FastAPI on :8000 |
| `poe frontend` | Start frontend only | Vite on :5173 |
| `poe test` | Run all tests | Backend + Frontend |
| `poe lint` | Lint all code | Ruff + ESLint |
| `poe format` | Format all code | Ruff + Prettier |
| `poe build` | Build for production | Both packages |

---

## Production Deployment

### 1. Build Frontend

```bash
cd frontend
pnpm build
```

### 2. Configure Production Environment

```bash
# Production .env
MEDIA_PATH=/mnt/hdd/media
CACHE_PATH=/mnt/ssd/cache
ENVIRONMENT=production
```

### 3. Run with Production Server

```bash
uv run uvicorn small_media.main:app --host 0.0.0.0 --port 8000
```

### 4. Cloudflare Zero Trust Setup

1. Create a Cloudflare Tunnel pointing to `localhost:8000`
2. Configure Access policies in Cloudflare Zero Trust dashboard
3. Access via your configured domain

---

## Docker (Alternative)

```bash
# Build image
docker build -t small-media .

# Run with volume mounts
docker run -d \
  -p 8000:8000 \
  -v /path/to/media:/media:ro \
  -v /path/to/cache:/cache \
  -e MEDIA_PATH=/media \
  -e CACHE_PATH=/cache \
  small-media
```

---

## Troubleshooting

### FFmpeg not found

```bash
# Verify FFmpeg installation
ffmpeg -version

# If not installed, install via package manager
```

### Permission denied on media files

```bash
# Ensure the user running the server has read access
ls -la /path/to/media
```

### Cache directory issues

```bash
# Ensure cache directory exists and is writable
mkdir -p /path/to/cache
chmod 755 /path/to/cache
```
