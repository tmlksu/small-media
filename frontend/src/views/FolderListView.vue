<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFolderStore } from '../stores/folder'

const router = useRouter()
const folderStore = useFolderStore()

onMounted(() => {
  folderStore.loadRootFolders()
})

function navigateToFolder(path: string) {
  router.push(`/folder/${path}`)
}
</script>

<template>
  <div class="folder-list-view">
    <header class="header">
      <h1 class="title">Small Media</h1>
      <p class="subtitle">Your private media library</p>
    </header>

    <div v-if="folderStore.isLoading" class="loading">
      <span>Loading...</span>
    </div>

    <div v-else-if="folderStore.error" class="error">
      {{ folderStore.error }}
    </div>

    <div v-else-if="folderStore.folders.length === 0" class="empty">
      <p>No folders found</p>
      <p class="hint">Add media files to your configured MEDIA_PATH</p>
    </div>

    <ul v-else class="folder-grid">
      <li
        v-for="folder in folderStore.folders"
        :key="folder.path"
        class="folder-card"
        :class="{ 'has-audio': folder.has_audio }"
        @click="navigateToFolder(folder.path)"
      >
        <div class="folder-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-15a3 3 0 00-3 3V18a3 3 0 003 3h15zM1.5 10.146V6a3 3 0 013-3h5.379a2.25 2.25 0 011.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 013 3v1.146A4.483 4.483 0 0019.5 9h-15a4.483 4.483 0 00-3 1.146z" />
          </svg>
        </div>
        <div class="folder-info">
          <span class="folder-name">{{ folder.name }}</span>
          <span class="folder-meta">
            <template v-if="folder.has_audio">♫ Audio</template>
            <template v-else-if="folder.subfolder_count > 0">
              {{ folder.subfolder_count }} folder{{ folder.subfolder_count > 1 ? 's' : '' }}
            </template>
            <template v-else>Empty</template>
          </span>
        </div>
        <div class="folder-arrow">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" d="M16.28 11.47a.75.75 0 010 1.06l-7.5 7.5a.75.75 0 01-1.06-1.06L14.69 12 7.72 5.03a.75.75 0 011.06-1.06l7.5 7.5z" clip-rule="evenodd" />
          </svg>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.folder-list-view {
  padding: var(--spacing-lg);
  max-width: 800px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: var(--text-secondary);
  margin-top: var(--spacing-xs);
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  margin-top: var(--spacing-sm);
}

.folder-grid {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.folder-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.folder-card:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-primary);
  transform: translateX(4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.folder-card.has-audio {
  border-left: 3px solid var(--accent-primary);
}

.folder-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: var(--border-radius-sm);
  color: var(--accent-primary);
}

.folder-icon svg {
  width: 24px;
  height: 24px;
}

.folder-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.folder-name {
  font-weight: 500;
  font-size: var(--font-size-md);
}

.folder-meta {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.folder-arrow {
  width: 24px;
  height: 24px;
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.folder-card:hover .folder-arrow {
  color: var(--accent-primary);
  transform: translateX(4px);
}
</style>
