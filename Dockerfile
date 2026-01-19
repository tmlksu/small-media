# Build stage for frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Production stage
FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy Python project files
COPY pyproject.toml README.md ./
COPY backend/ ./backend/

# Install Python dependencies (no --frozen since we don't commit uv.lock)
RUN uv sync --no-dev

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directories for media and cache
RUN mkdir -p /media /cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MEDIA_PATH=/media
ENV CACHE_PATH=/cache
ENV HOST=0.0.0.0
ENV PORT=7300

WORKDIR /app/backend/src

# Expose port
EXPOSE 7300

# Run the application
CMD ["uv", "run", "uvicorn", "small_media.main:app", "--host", "0.0.0.0", "--port", "7300"]
