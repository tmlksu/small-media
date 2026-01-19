# Small Media

A self-hosted private media player for audio files with on-the-fly transcoding and folder-based playlist management.

## Features

- 🎵 **Multi-format support**: wav, mp3, m4a, mp4, flac, ogg
- 🔄 **On-the-fly transcoding**: Convert to MP3 with intelligent caching
- 📁 **Folder-based playlists**: Organize by physical folder structure
- ↕️ **Drag-and-drop reordering**: Non-destructive playlist management
- 🔒 **Privacy-focused**: Hidden track titles in OS media controls
- 🌐 **Cloudflare Zero Trust ready**: Secure remote access

## Quick Start

```bash
# Install dependencies
uv sync
cd frontend && pnpm install && cd ..

# Configure
cp .env.example .env
# Edit .env with your paths

# Run development servers
poe dev
```

See [docs/INSTALLATION.md](./docs/INSTALLATION.md) for detailed setup instructions.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + TypeScript + Pinia |
| Backend | Python + FastAPI |
| Transcoding | FFmpeg |
| Package Manager | uv (Python), pnpm (Node.js) |
| Task Runner | Poe the Poet |

## Documentation

- [Installation Guide](./docs/INSTALLATION.md)
- [Specification](./docs/SPECIFICATION.md)
- [API Reference](./docs/api/openapi.yaml)
- [Architecture Decisions](./docs/adr/)

## Project Structure

```
small-media/
├── docs/           # Documentation
├── backend/        # Python FastAPI backend
├── frontend/       # Vue 3 frontend
└── pyproject.toml  # Python config & poe tasks
```

## License

MIT
