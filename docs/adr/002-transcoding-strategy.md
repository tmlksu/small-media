# ADR-002: Hybrid Transcoding Strategy

## Status
Accepted

## Context

We need to serve audio files in various formats (wav, flac, ogg, m4a, mp4) to web browsers. The target hardware (Intel N150, 16GB RAM, SSD+HDD) has limited CPU power but adequate storage.

Options considered:
1. **Pre-transcode all files**: Convert everything upfront
2. **Real-time transcoding**: Convert on every request
3. **Hybrid**: Transcode on first access, cache for future

## Decision

Implement **hybrid transcoding with caching**:

1. On audio request, generate cache key: `hash(filepath + mtime + output_settings)`
2. Check if cached version exists on SSD
3. If cached: serve directly
4. If not cached:
   - Start FFmpeg transcoding
   - Stream output to client while simultaneously writing to cache
   - Future requests serve from cache

### Special Cases
- **MP3 files with acceptable bitrate**: Passthrough without transcoding
- **Cache invalidation**: Automatic via mtime in cache key

### FFmpeg Settings
```bash
# Primary: VBR V2 (~190kbps)
ffmpeg -i input -codec:a libmp3lame -q:a 2 -f mp3 output

# Fallback: CBR 192kbps (if VBR causes issues)
ffmpeg -i input -codec:a libmp3lame -b:a 192k -f mp3 output
```

## Consequences

### Positive
- First-time listeners experience only slight initial delay
- Subsequent plays are instant (cache hit)
- No upfront processing time needed
- Storage efficient (only cache what's actually played)
- MP3 passthrough saves CPU for already-compatible files

### Negative
- First playback of large files may have noticeable start delay
- Cache can grow large if many files are played
- Need to implement cache eviction strategy eventually

### Neutral
- SSD recommended for cache to maximize performance
- Cache key includes output settings, allowing format changes
