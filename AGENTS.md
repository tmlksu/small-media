# AGENTS.md - LLM Agent Guidelines

This document defines the standards and practices for LLM agents (AI coding assistants) working on this project.

---

## Project Context

**Small Media** is a self-hosted private media player for audio files (Podcasts, Drama CDs, etc.) with on-the-fly transcoding, folder-based playback, and privacy-focused features.

### Domain Knowledge
- **Self-hosted media streaming**: Serve private audio content via Cloudflare Zero Trust
- **Folder-based organization**: Physical folder structure = playlist/album units
- **Privacy-first**: Hide track titles in OS media controls, no cloud storage
- **Transcoding**: Convert wav/flac/ogg to MP3 on-the-fly with caching

### Communication Language
- **Primary language with users: Japanese (日本語)**
- Technical terms may remain in English
- Code comments and documentation: English preferred

---

## Technology Stack Rules

### Frontend (Vue 3 + Pinia + TypeScript)
- Use **Composition API** with `<script setup>` syntax
- State management via **Pinia stores** (not Vuex)
- Use `ref()` and `computed()` for reactivity
- Prefer composables (`useXxx()`) for reusable logic
- Use **Media Session API** for background playback control

### Backend (Python + FastAPI)
- Use **FastAPI** for async HTTP API
- Use **FFmpeg** (via subprocess or ffmpeg-python) for transcoding
- Use **uv** for package management
- Use **Poe the Poet** (poethepoet) for task running
- Keep handlers small; extract business logic to services

### Shared Patterns
- Define types clearly (TypeScript interfaces / Python dataclasses/Pydantic)
- Use `async/await` for asynchronous operations
- Error responses: `{ "error": string, "details"?: unknown }`

---

## Project Structure

### Directory Layout

```
small-media/
├── AGENTS.md                 # This file
├── README.md                 # Project overview
├── pyproject.toml            # Python dependencies & poe tasks
├── docs/
│   ├── README.md             # Documentation overview
│   ├── INSTALLATION.md       # Setup instructions
│   ├── SPECIFICATION.md      # Detailed specifications
│   ├── adr/                  # Architecture Decision Records
│   │   └── NNN-title.md
│   ├── specs/                # Feature specifications
│   │   └── *.md
│   ├── api/                  # API documentation
│   │   └── openapi.yaml
│   └── issues/               # Known issues & TODOs
│       └── *.md
├── backend/                  # Python FastAPI backend
│   ├── src/
│   │   └── small_media/
│   └── tests/
└── frontend/                 # Vue 3 frontend
    ├── src/
    └── tests/
```

### Living Documents

- **ADRs (Architecture Decision Records)**: Document significant architectural decisions with context, decision, and consequences
- **Specs**: Feature specifications that evolve with the project
- Keep documents up-to-date when making related changes

---

## Development Environment

### Package Management (uv)

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Add a new dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>
```

### Task Running (Poe the Poet)

All common tasks are defined in `pyproject.toml`:

```bash
# Run development server
poe dev

# Run tests
poe test

# Lint code
poe lint

# Format code
poe format

# Build for production
poe build
```

---

## Coding Practices

### General Principles

1. **DRY (Don't Repeat Yourself)**
   - Extract reusable logic into functions/composables
   - Use shared types across frontend and backend
   - Centralize configuration values

2. **KISS (Keep It Simple, Stupid)**
   - Prefer simple, readable solutions over clever ones
   - Break complex functions into smaller, focused units

3. **YAGNI (You Aren't Gonna Need It)**
   - Don't implement features "just in case"
   - Add complexity only when required

4. **Single Responsibility Principle**
   - Each module/function should do one thing well
   - Separate concerns clearly

### No Hardcoding

**❌ Avoid:**
```python
# Hardcoded paths
MEDIA_PATH = "/home/user/music"

# Hardcoded values
BITRATE = 192

# Magic numbers
timeout = 30
```

**✅ Prefer:**
```python
# Environment variable with default
MEDIA_PATH = os.getenv("MEDIA_PATH", "/media")

# Configuration
BITRATE = settings.audio_bitrate

# Named constants
API_TIMEOUT_SECONDS = 30
```

### Type Safety

- **Python**: Use type hints, Pydantic models, `mypy` for static checking
- **TypeScript**: Use `strict: true`, define interfaces for all data structures
- Avoid `Any` type; use `Unknown` with type guards if needed

---

## Testing Guidelines

### Core Principle: No Shortcut Tests

Tests must exercise the **actual code paths** used in production.

**❌ Anti-patterns:**
```python
# Special flag that changes behavior for tests
if os.getenv("TEST_MODE"):
    return mock_response

# Bypassing validation for tests
skip_validation = os.getenv("ENV") == "test"
```

**✅ Correct approach:**
- Test through the same interfaces users/clients use
- Use dependency injection to substitute real services with test doubles
- Configure, don't code, test-specific behavior

### Test Types

1. **Unit Tests**: Test individual functions/components in isolation
2. **Integration Tests**: Test interactions between modules (API endpoints, transcoding pipeline)
3. **E2E Tests**: Test full user workflows through the actual UI

---

## FFmpeg / Transcoding Guidelines

### Command Patterns

```bash
# VBR MP3 (recommended)
ffmpeg -i input.wav -codec:a libmp3lame -q:a 2 output.mp3

# CBR MP3 (fallback)
ffmpeg -i input.wav -codec:a libmp3lame -b:a 192k output.mp3

# Stream to stdout (for HTTP streaming)
ffmpeg -i input.wav -codec:a libmp3lame -q:a 2 -f mp3 pipe:1
```

### Caching Strategy

1. Generate cache key from: `hash(filepath + mtime + output_settings)`
2. Check cache before transcoding
3. Stream from cache if available
4. Transcode and cache on first access

---

## Configuration Management

### Environment Variables

All configurable values should be loaded from environment or `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `MEDIA_PATH` | Root path to media files | `/media` |
| `CACHE_PATH` | Path for transcoded cache | `/cache` |
| `AUDIO_BITRATE` | Output MP3 bitrate (kbps) | `192` |
| `AUDIO_QUALITY` | LAME VBR quality (0-9) | `2` |

### Configuration File

Create `.env.example` documenting all required variables.

---

## Error Handling

- Handle errors gracefully with user-friendly messages
- Log errors with sufficient context for debugging
- Don't expose internal error details to end users
- Use typed error classes when appropriate

```python
class SmallMediaError(Exception):
    """Base exception for Small Media"""
    pass

class TranscodeError(SmallMediaError):
    """Error during audio transcoding"""
    pass

class FileNotFoundError(SmallMediaError):
    """Requested media file not found"""
    pass
```

---

## Security

- Never commit secrets or API keys
- Use `.gitignore` for sensitive files (`.env`, cache directories)
- Validate all user input (especially file paths to prevent directory traversal)
- Sanitize output to prevent XSS
- Rely on Cloudflare Zero Trust for authentication

---

## Commit and Change Guidelines

1. **Atomic Changes**: Each commit should represent one logical change
2. **Update Documentation**: When changing behavior, update related docs
3. **Test Before Committing**: Verify changes work as expected
4. **Clear Descriptions**: Explain *why* not just *what*
