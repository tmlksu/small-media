# ADR-003: YAML Playlist Format

## Status
Accepted

## Context

Users need to reorder tracks within folders and mark tracks to skip. The solution must be:
- Non-destructive (don't modify original audio files)
- Human-readable for manual editing
- Simple to parse and update programmatically
- Stored alongside the media files

Options considered:
1. **JSON file**: Machine-friendly but less human-readable
2. **YAML file**: Human-readable and widely supported
3. **SQLite database**: Powerful but overkill for this use case
4. **M3U playlist**: Standard but limited metadata support

## Decision

Use **YAML format** with the filename `.small-media-playlist.yaml` in each folder.

### Format Specification

```yaml
# .small-media-playlist.yaml
version: 1
tracks:
  - filename: track_05.wav
    skip: false
  - filename: track_01.wav
    skip: false
  - filename: track_02.wav
    skip: true
# Files not in this list appear after listed files in natural sort order
```

### Behavior Rules

1. **Listed tracks**: Appear in the order specified
2. **Unlisted tracks**: Appear after listed tracks, in natural sort order
3. **Skip flag**: When `true`, track is skipped during sequential playback
4. **Missing files**: Entries for non-existent files are ignored (no error)
5. **File creation**: Created/updated when user reorders via WebUI

### WebUI Interaction

1. User drags track to new position
2. Frontend sends `PUT /api/folders/{path}/playlist` with new order
3. Backend writes updated `.small-media-playlist.yaml`
4. File is created if it doesn't exist

## Consequences

### Positive
- Human-readable: users can manually edit if needed
- Non-destructive: original files remain untouched
- Portable: playlist travels with the folder
- Simple: easy to parse with standard YAML libraries
- Extensible: can add more metadata fields later

### Negative
- Hidden files may be missed by users
- YAML parsing is slightly slower than JSON
- No standard playlist format (custom to this app)

### Neutral
- Requires YAML library (PyYAML for Python)
- One playlist file per folder (not global playlists)
