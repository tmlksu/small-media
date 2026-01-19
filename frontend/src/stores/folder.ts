/**
 * Folder navigation store
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FolderItem, AudioFile } from '../types'
import { getRootFolders, getFolderContents } from '../api/client'

export const useFolderStore = defineStore('folder', () => {
    // State
    const currentPath = ref<string>('')
    const currentName = ref<string>('Root')
    const folders = ref<FolderItem[]>([])
    const files = ref<AudioFile[]>([])
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Getters
    const isRoot = computed(() => currentPath.value === '')
    const hasAudioFiles = computed(() => files.value.length > 0)
    const hasFolders = computed(() => folders.value.length > 0)

    // Actions
    async function loadRootFolders() {
        isLoading.value = true
        error.value = null

        try {
            const response = await getRootFolders()
            folders.value = response.folders
            files.value = []
            currentPath.value = ''
            currentName.value = 'Root'
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to load folders'
        } finally {
            isLoading.value = false
        }
    }

    async function loadFolder(path: string) {
        isLoading.value = true
        error.value = null

        try {
            const contents = await getFolderContents(path)
            folders.value = contents.folders
            files.value = contents.files
            currentPath.value = contents.path
            currentName.value = contents.name
        } catch (e) {
            error.value = e instanceof Error ? e.message : 'Failed to load folder'
        } finally {
            isLoading.value = false
        }
    }

    function getParentPath(): string {
        if (!currentPath.value) return ''
        const parts = currentPath.value.split('/')
        parts.pop()
        return parts.join('/')
    }

    return {
        // State
        currentPath,
        currentName,
        folders,
        files,
        isLoading,
        error,

        // Getters
        isRoot,
        hasAudioFiles,
        hasFolders,

        // Actions
        loadRootFolders,
        loadFolder,
        getParentPath,
    }
})
