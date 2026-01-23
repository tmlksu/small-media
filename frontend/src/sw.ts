import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst, CacheFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'
import { RangeRequestsPlugin } from 'workbox-range-requests'

declare let self: ServiceWorkerGlobalScope

cleanupOutdatedCaches()

precacheAndRoute(self.__WB_MANIFEST)

// API Folders Strategy - Network First
registerRoute(
    /^https?:\/\/.*\/api\/folders/,
    new NetworkFirst({
        cacheName: 'api-folders',
        plugins: [
            new ExpirationPlugin({
                maxEntries: 50,
                maxAgeSeconds: 60 * 60, // 1 hour
            }),
        ],
    })
)

// Audio Stream Strategy - Cache First
registerRoute(
    /^https?:\/\/.*\/api\/stream\//,
    new CacheFirst({
        cacheName: 'audio-cache',
        plugins: [
            new ExpirationPlugin({
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 1 week
            }),
            new RangeRequestsPlugin(),
        ],
    })
)

// Navigation requests are explicitly NOT handled to allow CFZT redirects
