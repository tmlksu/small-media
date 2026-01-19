/**
 * API types matching backend Pydantic models
 */

export interface FolderItem {
    name: string
    path: string // URL-encoded relative path
    has_audio: boolean
    subfolder_count: number
}

export interface AudioFile {
    filename: string
    path: string // URL-encoded relative path for streaming
    format: string
    size: number // bytes
}

export interface FolderContents {
    path: string
    name: string
    folders: FolderItem[]
    files: AudioFile[]
}

export interface FolderListResponse {
    folders: FolderItem[]
}

export interface PlaylistTrack {
    filename: string
    path: string
    skip: boolean
    duration: number | null
}

export interface Playlist {
    path: string
    tracks: PlaylistTrack[]
}

export interface PlaylistTrackUpdate {
    filename: string
    skip: boolean
}

export interface PlaylistUpdate {
    tracks: PlaylistTrackUpdate[]
}

export interface AudioInfo {
    filename: string
    duration: number
    format: string
    bitrate: number | null
    sample_rate: number | null
    channels: number | null
}

export interface ErrorResponse {
    error: string
    details: string | null
}
