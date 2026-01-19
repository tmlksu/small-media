<script setup lang="ts">
import { computed } from 'vue'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

const progressPercent = computed(() => playerStore.progress * 100)

function formatTime(seconds: number): string {
  if (!isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleProgressClick(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const x = event.clientX - rect.left
  const progress = x / rect.width
  playerStore.seekToProgress(progress)
}
</script>

<template>
  <div class="player-bar" :class="{ 'has-track': playerStore.currentTrack }">
    <div class="player-content">
      <!-- Progress bar -->
      <div 
        class="progress-bar" 
        @click="handleProgressClick"
      >
        <div 
          class="progress-fill" 
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>

      <div class="player-main">
        <!-- Track info -->
        <div class="track-info">
          <template v-if="playerStore.currentTrack">
            <span class="track-name">{{ playerStore.currentTrack.filename }}</span>
            <span class="track-time">
              {{ formatTime(playerStore.currentTime) }} / {{ formatTime(playerStore.duration) }}
            </span>
          </template>
          <template v-else>
            <span class="track-name placeholder">No track playing</span>
          </template>
        </div>

        <!-- Controls -->
        <div class="controls">
          <button 
            class="control-btn" 
            :disabled="!playerStore.hasPrevious"
            @click="playerStore.previous()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.195 18.44c1.25.713 2.805-.19 2.805-1.629v-2.34l6.945 3.968c1.25.714 2.805-.188 2.805-1.628V8.688c0-1.44-1.555-2.342-2.805-1.628L12 11.03v-2.34c0-1.44-1.555-2.343-2.805-1.629l-7.108 4.062c-1.26.72-1.26 2.536 0 3.256l7.108 4.061z" />
            </svg>
          </button>

          <button 
            class="control-btn play-btn" 
            @click="playerStore.toggle()"
          >
            <svg v-if="playerStore.isPlaying" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" d="M6.75 5.25a.75.75 0 01.75-.75H9a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H7.5a.75.75 0 01-.75-.75V5.25zm7.5 0A.75.75 0 0115 4.5h1.5a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H15a.75.75 0 01-.75-.75V5.25z" clip-rule="evenodd" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.348c1.295.712 1.295 2.573 0 3.285L7.28 19.991c-1.25.687-2.779-.217-2.779-1.643V5.653z" clip-rule="evenodd" />
            </svg>
          </button>

          <button 
            class="control-btn" 
            :disabled="!playerStore.hasNext"
            @click="playerStore.next()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M5.055 7.06c-1.25-.714-2.805.189-2.805 1.628v8.123c0 1.44 1.555 2.342 2.805 1.628L12 14.471v2.34c0 1.44 1.555 2.342 2.805 1.628l7.108-4.061c1.26-.72 1.26-2.536 0-3.256L14.805 7.06C13.555 6.346 12 7.25 12 8.688v2.34L5.055 7.06z" />
            </svg>
          </button>
        </div>

        <!-- Volume (desktop only) -->
        <div class="volume-control">
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.01"
            :value="playerStore.volume"
            @input="(e) => playerStore.setVolume(parseFloat((e.target as HTMLInputElement).value))"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  backdrop-filter: blur(20px);
  z-index: 100;
  transform: translateY(100%);
  transition: transform var(--transition-normal);
}

.player-bar.has-track {
  transform: translateY(0);
}

.player-content {
  max-width: 1200px;
  margin: 0 auto;
}

.progress-bar {
  height: 4px;
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: height var(--transition-fast);
}

.progress-bar:hover {
  height: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 2px;
  transition: width 100ms linear;
}

.player-main {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
}

.track-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.track-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-name.placeholder {
  color: var(--text-muted);
}

.track-time {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.control-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: var(--text-primary);
  transition: all var(--transition-fast);
}

.control-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
}

.control-btn:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
}

.control-btn svg {
  width: 20px;
  height: 20px;
}

.control-btn.play-btn {
  width: 48px;
  height: 48px;
  background: var(--accent-primary);
}

.control-btn.play-btn:hover {
  background: var(--accent-secondary);
  box-shadow: 0 0 20px var(--accent-glow);
}

.control-btn.play-btn svg {
  width: 24px;
  height: 24px;
}

.volume-control {
  display: none;
  width: 100px;
}

@media (min-width: 768px) {
  .volume-control {
    display: block;
  }
}

.volume-control input[type="range"] {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-tertiary);
  border-radius: 2px;
  cursor: pointer;
}

.volume-control input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: var(--accent-primary);
  border-radius: 50%;
  cursor: pointer;
}
</style>
