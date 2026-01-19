<script setup lang="ts">
import { RouterView } from 'vue-router'
import PlayerBar from './components/PlayerBar.vue'
</script>

<template>
  <div class="app">
    <main class="main-content">
      <RouterView />
    </main>
    <PlayerBar />
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 80px; /* Space for player bar */
}
</style>
