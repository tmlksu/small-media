# ADR-001: Technology Stack Selection

## Status
Accepted

## Context

We need to build a self-hosted media player with the following requirements:
- On-the-fly audio transcoding
- Folder-based playlist management
- Web-based UI for mobile access
- Privacy-focused background playback
- Deployment via Cloudflare Zero Trust

We considered various technology options for both frontend and backend.

## Decision

### Backend: Python + FastAPI
- **Framework**: FastAPI for async HTTP handling
- **Package Manager**: uv (fast, modern Python package management)
- **Task Runner**: Poe the Poet (poethepoet)
- **Transcoding**: FFmpeg via subprocess

**Rationale:**
- Python has excellent FFmpeg bindings and subprocess handling
- FastAPI provides async streaming support needed for audio delivery
- uv is significantly faster than pip/poetry for dependency resolution
- Poe provides clean task definition in pyproject.toml

### Frontend: Vue 3 + TypeScript + Pinia
- **Framework**: Vue 3 with Composition API
- **State Management**: Pinia
- **Build Tool**: Vite
- **Package Manager**: pnpm

**Rationale:**
- Vue 3 Composition API provides clean, reusable logic
- Pinia is the official Vue state management solution
- Vite provides fast development experience
- TypeScript ensures type safety

### Audio Delivery: MP3 via HTTP
- **Output Format**: MP3 (LAME VBR V2)
- **Delivery**: Standard HTTP streaming

**Rationale:**
- MP3 has universal browser support including iOS Safari
- VBR provides good quality-to-size ratio
- HTTP streaming is simple and works through CFZT

## Consequences

### Positive
- uv significantly speeds up dependency installation
- FastAPI's async support enables efficient concurrent streaming
- Vue 3 Composition API allows clean separation of concerns
- MP3 compatibility eliminates browser-specific issues

### Negative
- Python subprocess for FFmpeg adds process overhead
- No HLS/DASH means no adaptive bitrate streaming
- Single output format limits flexibility

### Neutral
- Requires FFmpeg system dependency
- Need to maintain two package ecosystems (Python + Node.js)
