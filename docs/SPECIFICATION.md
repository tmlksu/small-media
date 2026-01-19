# Small Media - Specification

## Overview

**Small Media** is a self-hosted private media player designed for:

- Playing multi-file audio content (Podcasts, Drama CDs, etc.)
- On-the-fly transcoding to MP3 format
- Folder-based playlist management with drag-and-drop reordering
- Privacy-focused background playback (hidden track titles)
- Deployment via Cloudflare Zero Trust

---

## System Requirements

### Hardware

| Component | Specification | Notes |
|-----------|---------------|-------|
| CPU | Intel N150 or equivalent | Low-power, sufficient for MP3 encoding |
| RAM | 16GB | Comfortable for concurrent transcoding |
| Storage | SSD + HDD | SSD for cache, HDD for media files |

### Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| FFmpeg | 6.0+ | Audio transcoding |
| uv | Latest | Python package management |

---

## Supported Audio Formats

### Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | `.wav` | Uncompressed, requires transcoding |
| MP3 | `.mp3` | Passthrough if compatible bitrate |
| M4A | `.m4a` | AAC audio container |
| MP4 | `.mp4` | Audio-only expected |
| FLAC | `.flac` | Lossless, requires transcoding |
| Ogg | `.ogg` | Vorbis audio |

### Output Format

| Property | Value | Notes |
|----------|-------|-------|
| Codec | MP3 (LAME) | Maximum compatibility |
| Mode | VBR V2 | ~190kbps average |
| Fallback | CBR 192kbps | For seek issues |

---

## Core Features

### 1. Folder-Based Navigation

- Physical folder structure = album/playlist unit
- Recursive folder listing from configured media root
- Only show folders containing supported audio files

### 2. Transcoding Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Source File │────▶│ Check Cache │────▶│ Serve Cache │
│ (wav/flac)  │     │             │     │ (if exists) │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │ miss
                          ▼
                   ┌─────────────┐     ┌─────────────┐
                   │  Transcode  │────▶│ Cache & Serve│
                   │  (FFmpeg)   │     │             │
                   └─────────────┘     └─────────────┘
```

**Behavior:**
- MP3 files with acceptable bitrate: passthrough (no transcoding)
- Other formats: transcode to MP3 VBR V2
- Cache transcoded files on SSD
- Cache key: `hash(filepath + mtime + output_settings)`

### 3. Playlist Management

**File:** `.small-media-playlist.yaml`

```yaml
# Located in each folder
version: 1
tracks:
  - filename: track_05.wav
    skip: false
  - filename: track_01.wav
    skip: false
  - filename: track_02.wav
    skip: true   # Will be skipped during playback
# Files not listed appear after listed files in natural order
```

**Features:**
- Non-destructive: original files unchanged
- Drag-and-drop reordering via WebUI
- Skip flag for individual tracks
- Unlisted files appear at end in natural sort order

### 4. Privacy-Focused Playback

**Media Session API Configuration:**

| Property | Value |
|----------|-------|
| Title | "Small Media" |
| Artist | (empty) |
| Album | (empty) |
| Artwork | Generic icon |

**Behavior:**
- Lock screen / notification shows generic "Small Media" title
- Actual track info only visible in WebUI
- Background audio continues when browser minimized

### 5. Session-Based Resume

- Playback position remembered within browser session
- Position lost on page refresh (by design)
- No persistent resume across sessions

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/folders` | GET | List root folders |
| `GET /api/folders/{path}` | GET | List contents of folder |
| `GET /api/folders/{path}/playlist` | GET | Get playlist with order & skip flags |
| `PUT /api/folders/{path}/playlist` | PUT | Update playlist order & skip flags |
| `GET /api/stream/{path}` | GET | Stream audio (transcoded if needed) |
| `GET /api/stream/{path}/info` | GET | Get audio metadata (duration, etc.) |

See [api/openapi.yaml](./api/openapi.yaml) for full API specification.

---

## Security Model

### Authentication

- Cloudflare Zero Trust handles all authentication
- No application-level auth required
- Server only accessible via CFZT tunnel

### Authorization

- All authenticated users have full access
- No per-user restrictions (single-user design)

### Path Safety

- Validate all file paths to prevent directory traversal
- Restrict access to configured `MEDIA_PATH` only
- Reject paths containing `..` or absolute paths

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MEDIA_PATH` | Yes | - | Root path to media files |
| `CACHE_PATH` | Yes | - | Path for transcoded cache |
| `AUDIO_QUALITY` | No | `2` | LAME VBR quality (0-9) |
| `AUDIO_BITRATE` | No | `192` | CBR fallback bitrate |
| `ALLOWED_EXTENSIONS` | No | `wav,mp3,m4a,mp4,flac,ogg` | Comma-separated list |

---

## UI/UX Design

### Navigation Flow

```
┌─────────────────────────────────┐
│ 📁 Folder List                  │
│ ─────────────────────────────── │
│ 📂 Drama CD Vol.1               │
│ 📂 Podcast 2024-01              │
│ 📂 Music Collection             │
└─────────────────────────────────┘
              │ tap
              ▼
┌─────────────────────────────────┐
│ ◀ Back    Drama CD Vol.1       │
│ ─────────────────────────────── │
│ ≡ Track 1          ▶ [skip □]  │
│ ≡ Track 2          ▶ [skip □]  │
│ ≡ Track 3          ▶ [skip ☑]  │
│ ─────────────────────────────── │
│ advancement bar ─●──────────── │
│      ⏮️  ▶️  ⏭️                  │
└─────────────────────────────────┘
```

### Mobile Considerations

- Touch-friendly drag handles for reordering
- Large tap targets for playback controls
- Responsive layout for various screen sizes
- PWA support for home screen installation

---

## Development Phases

### Phase 1: Foundation
- [ ] Project setup (uv, poe, FastAPI, Vue)
- [ ] Folder listing API
- [ ] Basic audio streaming (no transcoding)
- [ ] Simple folder/file browser UI

### Phase 2: Transcoding
- [ ] FFmpeg integration
- [ ] On-the-fly transcoding
- [ ] Cache management
- [ ] MP3 passthrough detection

### Phase 3: Playlist Management
- [ ] `.small-media-playlist.yaml` parsing
- [ ] Drag-and-drop reordering UI
- [ ] Skip flag support
- [ ] Playlist persistence

### Phase 4: Playback Polish
- [ ] Media Session API integration
- [ ] Background playback
- [ ] Session-based resume
- [ ] PWA manifest

### Phase 5: Production
- [ ] Docker packaging
- [ ] CFZT integration guide
- [ ] Performance optimization
- [ ] Documentation completion
