/**
 * Custom Service Worker for Small Media PWA
 *
 * CRITICAL: This Service Worker does NOT intercept navigation requests.
 * This allows Cloudflare Zero Trust 302 redirects to work correctly.
 *
 * Only API and streaming requests are cached.
 */

/// <reference lib="webworker" />

import { precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst, CacheFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'

declare let self: ServiceWorkerGlobalScope

// Precache static assets generated during build
precacheAndRoute(self.__WB_MANIFEST)

// API folders - NetworkFirst strategy
// Try network first, fallback to cache if offline
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/folders'),
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

// Audio streaming - CacheFirst strategy
// Use cache first for performance, with range request support
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/stream/'),
  new CacheFirst({
    cacheName: 'audio-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 60 * 60 * 24 * 7, // 1 week
      }),
    ],
  })
)

// CRITICAL: Do NOT intercept navigation requests
// This event listener ensures navigation requests pass through to the browser,
// allowing Cloudflare Zero Trust to handle 302 redirects properly.
self.addEventListener('fetch', (event: FetchEvent) => {
  // Navigation requests (page loads) must NOT be intercepted
  // to allow CFZT authentication flow to work
  if (event.request.mode === 'navigate') {
    // Do NOT call event.respondWith()
    // Let the browser handle the request directly
    return
  }

  // All other requests (API, streams, etc.) are handled by
  // the registerRoute() handlers above
})
