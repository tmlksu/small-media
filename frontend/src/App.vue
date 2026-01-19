<script setup lang="ts">
import { RouterView } from 'vue-router'
import PlayerBar from './components/PlayerBar.vue'
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="app">
    <main class="main-content">
      <RouterView />
    </main>
    <div class="bottom-container">
      <PlayerBar />
      <NavBar />
    </div>
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
  padding-bottom: 140px; /* Space for player bar + navbar */
}

.bottom-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
</style>
