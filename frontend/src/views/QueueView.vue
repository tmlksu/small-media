<script setup lang="ts">
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

function playTrack(index: number) {
  playerStore.playIndex(index)
}

function removeFromQueue(index: number) {
  playerStore.removeFromPlaylist(index)
}
</script>

<template>
  <div class="queue-view">
    <header class="header">
      <h1 class="title">Now Playing</h1>
    </header>

    <div v-if="playerStore.playlist.length === 0" class="empty">
      <p>Queue is empty</p>
      <p class="hint">Browse your library and add some tracks</p>
    </div>

    <ul v-else class="queue-list">
      <li
        v-for="(track, index) in playerStore.playlist"
        :key="track.path + index"
        class="queue-item"
        :class="{ 'is-current': index === playerStore.currentIndex }"
        @click="playTrack(index)"
      >
        <div class="track-number">{{ index + 1 }}</div>
        <div class="track-info">
          <span class="track-name">{{ track.filename }}</span>
        </div>
        <button class="remove-btn" @click.stop="removeFromQueue(index)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clip-rule="evenodd" />
          </svg>
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.queue-view {
  padding: var(--spacing-md);
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.title {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.empty {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--text-muted);
}

.hint {
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-sm);
}

.queue-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.queue-item:hover {
  background: var(--bg-tertiary);
}

.queue-item.is-current {
  background: var(--accent-glow);
  border-left: 3px solid var(--accent-primary);
}

.track-number {
  width: 24px;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.track-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.track-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.remove-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  border-radius: 50%;
  opacity: 0;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.queue-item:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}
</style>
