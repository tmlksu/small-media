# Installation Guide

This guide covers setting up Small Media for development and production.

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 20+ (for frontend)
- **FFmpeg**: 6.0+ (for transcoding)
- **uv**: Python package manager

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
npm install
cd ..
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit MEDIA_PATH and CACHE_PATH
```

Required environment variables:

```bash
MEDIA_PATH=/path/to/your/media   # HDD for media files
CACHE_PATH=/path/to/cache        # SSD for transcoded cache
```

### 5. Run Development Servers

```bash
# Using poe tasks
poe dev

# Or manually:
uv run poe backend   # Terminal 1
cd frontend && npm run dev   # Terminal 2
```

Visit `http://localhost:5173`

---

## Docker Deployment (Recommended)

### Quick Start with Docker Compose

```bash
# Create directories
mkdir -p media cache

# Start the application
docker compose up -d

# View logs
docker compose logs -f
```

The application will be available at `http://localhost:7300`

### Custom Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  small-media:
    volumes:
      # Mount your media directory
      - /path/to/your/media:/media:ro
      # Mount cache (ensure sufficient space)
      - /path/to/cache:/cache
    environment:
      - AUDIO_QUALITY=2
      - DEBUG=false
```

### Build and Run Manually

```bash
# Build image
docker build -t small-media .

# Run container
docker run -d \
  --name small-media \
  -p 7300:7300 \
  -v /path/to/media:/media:ro \
  -v /path/to/cache:/cache \
  small-media
```

---

## Production Deployment

### With Cloudflare Zero Trust

1. Run Docker container on port 7300
2. Create Cloudflare Tunnel pointing to `localhost:7300`
3. Configure Access policies in Cloudflare dashboard
4. Access via your domain

### Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name media.example.com;

    location / {
        proxy_pass http://localhost:7300;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Poe Tasks Reference

| Task | Description |
|------|-------------|
| `poe dev` | Start both servers |
| `poe backend` | Backend only |
| `poe frontend` | Frontend only |
| `poe test` | Run all tests |
| `poe lint` | Lint code |
| `poe build` | Production build |

---

## Troubleshooting

### FFmpeg not found

```bash
ffmpeg -version
# If not installed, install via package manager
```

### Permission denied

```bash
# Ensure read access to media files
ls -la /path/to/media

# Ensure write access to cache
mkdir -p /path/to/cache && chmod 755 /path/to/cache
```

### Docker health check failing

```bash
# Check container logs
docker compose logs small-media

# Verify health endpoint
curl http://localhost:7300/api/health
```
