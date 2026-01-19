<script setup lang="ts">
import { onMounted, watch, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFolderStore } from '../stores/folder'
import { usePlayerStore } from '../stores/player'
import { getPlaylist, updatePlaylist } from '../api/client'
import type { PlaylistTrack } from '../types'

const route = useRoute()
const router = useRouter()
const folderStore = useFolderStore()
const playerStore = usePlayerStore()

const playlist = ref<PlaylistTrack[]>([])
const isLoadingPlaylist = ref(false)
const draggedIndex = ref<number | null>(null)

const currentPath = computed(() => {
  const pathParam = route.params.path
  if (Array.isArray(pathParam)) {
    return pathParam.join('/')
  }
  return pathParam || ''
})

onMounted(() => {
  loadCurrentFolder()
})

watch(() => route.params.path, () => {
  loadCurrentFolder()
})

async function loadCurrentFolder() {
  const path = currentPath.value
  if (path) {
    await folderStore.loadFolder(path)
    await loadPlaylist()
  } else {
    folderStore.loadRootFolders()
    playlist.value = []
  }
}

async function loadPlaylist() {
  if (!currentPath.value || !folderStore.hasAudioFiles) return
  
  isLoadingPlaylist.value = true
  try {
    const response = await getPlaylist(currentPath.value)
    playlist.value = response.tracks
  } catch (e) {
    console.error('Failed to load playlist', e)
    // Fallback to files from folder
    playlist.value = folderStore.files.map(f => ({
      filename: f.filename,
      path: f.path,
      skip: false,
      duration: null,
    }))
  } finally {
    isLoadingPlaylist.value = false
  }
}

function goBack() {
  const parentPath = folderStore.getParentPath()
  if (parentPath) {
    router.push(`/folder/${parentPath}`)
  } else {
    router.push('/')
  }
}

function navigateToFolder(path: string) {
  router.push(`/folder/${path}`)
}

function playFile(index: number) {
  // Filter out skipped tracks
  const playableTracks = playlist.value.filter(t => !t.skip)
  const track = playlist.value[index]
  if (!track) return
  
  // Find the actual index in playable tracks
  const playableIndex = playableTracks.findIndex(t => t.path === track.path)
  
  playerStore.setPlaylist(
    playableTracks.map(t => ({
      filename: t.filename,
      path: t.path,
      format: t.filename.split('.').pop() || '',
      size: 0,
    })),
    playableIndex >= 0 ? playableIndex : 0
  )
}

function playAll() {
  const playableTracks = playlist.value.filter(t => !t.skip)
  if (playableTracks.length > 0) {
    playerStore.setPlaylist(
      playableTracks.map(t => ({
        filename: t.filename,
        path: t.path,
        format: t.filename.split('.').pop() || '',
        size: 0,
      })),
      0
    )
  }
}



// Drag and drop handlers
function onDragStart(index: number, event: DragEvent) {
  draggedIndex.value = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(index))
  }
}

function onDragOver(_index: number, event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

function onDrop(targetIndex: number, event: DragEvent) {
  event.preventDefault()
  if (draggedIndex.value === null || draggedIndex.value === targetIndex) {
    draggedIndex.value = null
    return
  }
  
  // Reorder playlist
  const items = [...playlist.value]
  const removed = items.splice(draggedIndex.value, 1)[0]
  if (removed) {
    items.splice(targetIndex, 0, removed)
    playlist.value = items
  }
  
  draggedIndex.value = null
  
  // Save to server
  savePlaylist()
}

function onDragEnd() {
  draggedIndex.value = null
}

async function toggleSkip(index: number) {
  const track = playlist.value[index]
  if (track) {
    track.skip = !track.skip
    await savePlaylist()
  }
}

async function savePlaylist() {
  if (!currentPath.value) return
  
  try {
    await updatePlaylist(currentPath.value, {
      tracks: playlist.value.map(t => ({
        filename: t.filename,
        skip: t.skip,
      })),
    })
  } catch (e) {
    console.error('Failed to save playlist', e)
  }
}
</script>

<template>
  <div class="folder-view">
    <header class="header">
      <button class="back-btn" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M7.72 12.53a.75.75 0 010-1.06l7.5-7.5a.75.75 0 111.06 1.06L9.31 12l6.97 6.97a.75.75 0 11-1.06 1.06l-7.5-7.5z" clip-rule="evenodd" />
        </svg>
        Back
      </button>
      <div class="header-info">
        <h1 class="title">{{ folderStore.currentName }}</h1>
      </div>
    </header>

    <div v-if="folderStore.isLoading" class="loading">
      <span>Loading...</span>
    </div>

    <div v-else-if="folderStore.error" class="error">
      {{ folderStore.error }}
    </div>

    <template v-else>
      <!-- Subfolders -->
      <section v-if="folderStore.hasFolders" class="section">
        <h2 class="section-title">Folders</h2>
        <ul class="folder-list">
          <li
            v-for="folder in folderStore.folders"
            :key="folder.path"
            class="folder-item"
            :class="{ 'has-audio': folder.has_audio }"
            @click="navigateToFolder(folder.path)"
          >
            <div class="item-icon folder-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-15a3 3 0 00-3 3V18a3 3 0 003 3h15z" />
              </svg>
            </div>
            <span class="item-name">{{ folder.name }}</span>
            <span class="item-meta" v-if="folder.has_audio">♫</span>
          </li>
        </ul>
      </section>

      <!-- Audio Files (Playlist) -->
      <section v-if="playlist.length > 0" class="section">
        <div class="section-header">
          <h2 class="section-title">Tracks</h2>
          <button class="btn btn-primary" @click="playAll">
            ▶ Play All
          </button>
        </div>
        <p class="reorder-hint">Drag to reorder • Click checkbox to skip</p>
        <ul class="track-list">
          <li
            v-for="(track, index) in playlist"
            :key="track.path"
            class="track-item"
            :class="{ 
              'is-playing': playerStore.currentTrack?.path === track.path,
              'is-skipped': track.skip,
              'is-dragging': draggedIndex === index,
            }"
            draggable="true"
            @dragstart="onDragStart(index, $event)"
            @dragover="onDragOver(index, $event)"
            @drop="onDrop(index, $event)"
            @dragend="onDragEnd"
          >
            <div class="drag-handle">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 9h18v2H3V9zm0 4h18v2H3v-2z"/>
              </svg>
            </div>
            <div class="track-number">{{ index + 1 }}</div>
            <div class="track-info" @click="playFile(index)">
              <span class="track-name">{{ track.filename }}</span>
            </div>
            <label class="skip-toggle" @click.stop>
              <input 
                type="checkbox" 
                :checked="track.skip"
                @change="toggleSkip(index)"
              />
              <span class="skip-label">Skip</span>
            </label>
            <button class="play-btn" @click="playFile(index)">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.348c1.295.712 1.295 2.573 0 3.285L7.28 19.991c-1.25.687-2.779-.217-2.779-1.643V5.653z" clip-rule="evenodd" />
              </svg>
            </button>
          </li>
        </ul>
      </section>

      <!-- Empty state -->
      <div v-if="!folderStore.hasFolders && playlist.length === 0" class="empty">
        <p>This folder is empty</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.folder-view {
  padding: var(--spacing-md);
  max-width: 800px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.back-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

.header-info {
  flex: 1;
}

.title {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.section {
  margin-bottom: var(--spacing-xl);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-md);
}

.section-header .section-title {
  margin-bottom: 0;
}

.reorder-hint {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  margin-bottom: var(--spacing-sm);
}

/* Folder List */
.folder-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.folder-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.folder-item:hover {
  background: var(--bg-tertiary);
}

.folder-item.has-audio {
  border-left: 2px solid var(--accent-primary);
}

.item-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
}

.item-icon svg {
  width: 20px;
  height: 20px;
}

.item-name {
  flex: 1;
  font-weight: 500;
}

.item-meta {
  color: var(--accent-primary);
  font-size: var(--font-size-sm);
}

/* Track List */
.track-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.track-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
}

.track-item:hover {
  background: var(--bg-tertiary);
}

.track-item.is-playing {
  background: var(--accent-glow);
  border: 1px solid var(--accent-primary);
}

.track-item.is-skipped {
  opacity: 0.5;
}

.track-item.is-skipped .track-name {
  text-decoration: line-through;
}

.track-item.is-dragging {
  opacity: 0.5;
  background: var(--accent-glow);
}

.drag-handle {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: grab;
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-handle svg {
  width: 16px;
  height: 16px;
}

.track-number {
  width: 24px;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.track-info {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.track-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.skip-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
}

.skip-toggle input {
  accent-color: var(--accent-primary);
}

.skip-label {
  display: none;
}

@media (min-width: 480px) {
  .skip-label {
    display: inline;
  }
}

.play-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border-radius: 50%;
  color: white;
  opacity: 0;
  transition: all var(--transition-fast);
}

.track-item:hover .play-btn {
  opacity: 1;
}

.play-btn svg {
  width: 16px;
  height: 16px;
}
</style>
