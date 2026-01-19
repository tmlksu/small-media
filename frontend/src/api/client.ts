/**
 * API client for Small Media backend
 */

import type {
    FolderContents,
    FolderListResponse,
    Playlist,
    PlaylistUpdate,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

class ApiError extends Error {
    status: number

    constructor(status: number, message: string) {
        super(message)
        this.name = 'ApiError'
        this.status = status
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new ApiError(response.status, error.error || 'Request failed')
    }
    return response.json()
}

/**
 * Get list of root folders
 */
export async function getRootFolders(): Promise<FolderListResponse> {
    const response = await fetch(`${API_BASE}/folders`)
    return handleResponse<FolderListResponse>(response)
}

/**
 * Get contents of a specific folder
 */
export async function getFolderContents(path: string): Promise<FolderContents> {
    const response = await fetch(`${API_BASE}/folders/${path}`)
    return handleResponse<FolderContents>(response)
}

/**
 * Get playlist for a folder
 */
export async function getPlaylist(path: string): Promise<Playlist> {
    const response = await fetch(`${API_BASE}/folders/${path}/playlist`)
    return handleResponse<Playlist>(response)
}

/**
 * Update playlist order and skip flags
 */
export async function updatePlaylist(
    path: string,
    data: PlaylistUpdate
): Promise<Playlist> {
    const response = await fetch(`${API_BASE}/folders/${path}/playlist`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    return handleResponse<Playlist>(response)
}

/**
 * Get stream URL for an audio file
 */
export function getStreamUrl(path: string): string {
    return `${API_BASE}/stream/${path}`
}

