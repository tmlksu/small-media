import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import './style.css'

// Routes
const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('./views/FolderListView.vue'),
    },
    {
        path: '/folder/:path(.*)*',
        name: 'folder',
        component: () => import('./views/FolderView.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
