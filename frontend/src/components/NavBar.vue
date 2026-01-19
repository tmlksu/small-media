<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/' || route.path.startsWith('/folder')
  }
  return route.path.startsWith(path)
}
</script>

<template>
  <nav class="navbar">
    <router-link to="/" class="nav-item" :class="{ active: isActive('/') }">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-15a3 3 0 00-3 3V18a3 3 0 003 3h15z" />
        <path fill-rule="evenodd" d="M1.5 9.832v1.793c0 1.036.84 1.875 1.875 1.875h17.25c1.035 0 1.875-.84 1.875-1.875V9.832a3 3 0 00-.722-1.952l-3.285-3.832A3 3 0 0016.215 3h-8.43a3 3 0 00-2.278 1.048L2.222 7.88A3 3 0 001.5 9.832z" clip-rule="evenodd" />
      </svg>
      <span>Explore</span>
    </router-link>
    <router-link to="/queue" class="nav-item" :class="{ active: isActive('/queue') }">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path fill-rule="evenodd" d="M2.25 6a3 3 0 013-3h13.5a3 3 0 013 3v12a3 3 0 01-3 3H5.25a3 3 0 01-3-3V6zm3.97.97a.75.75 0 011.06 0l2.25 2.25a.75.75 0 010 1.06l-2.25 2.25a.75.75 0 01-1.06-1.06l1.72-1.72-1.72-1.72a.75.75 0 010-1.06zm4.28 4.28a.75.75 0 000 1.5h5.25a.75.75 0 000-1.5h-5.25z" clip-rule="evenodd" />
      </svg>
      <span>Queue</span>
    </router-link>
  </nav>
</template>

<style scoped>
.navbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 24px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 11px;
  transition: color var(--transition-fast);
}

.nav-item svg {
  width: 22px;
  height: 22px;
}

.nav-item:hover,
.nav-item.active {
  color: var(--accent-primary);
}
</style>
