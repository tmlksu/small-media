/**
 * Custom Service Worker for Small Media PWA
 *
 * Handles Cloudflare Zero Trust (CFZT) authentication redirects.
 *
 * Problem: CFZT uses HTTP 302 redirects for authentication. Service Workers
 * cannot follow cross-origin 302 redirects via respondWith() - the browser
 * blocks them with ERR_BLOCKED_BY_CLIENT. precacheAndRoute also serves
 * cached index.html for navigation, bypassing the server entirely.
 *
 * Solution: For navigation requests, fetch with redirect:'manual' to detect
 * 302 redirects. When detected, return a synthetic HTML page that unregisters
 * the SW and reloads, allowing the browser to follow the 302 natively.
 * After CFZT login, the app re-registers the SW on next load.
 */

/// <reference lib="webworker" />

import { precache, addRoute, matchPrecache } from 'workbox-precaching'
import { registerRoute, NavigationRoute } from 'workbox-routing'
import { NetworkFirst, CacheFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'
import { RangeRequestsPlugin } from 'workbox-range-requests'

declare let self: ServiceWorkerGlobalScope

// Step 1: Precache static assets (without adding route yet)
precache(self.__WB_MANIFEST)

// Step 2: Navigation handler - detect CFZT auth redirects
const navigationHandler = async ({ request }: { request: Request }): Promise<Response> => {
    try {
        // redirect:'manual' prevents the browser from following 302s,
        // returning an opaqueredirect response instead
        const response = await fetch(request, { redirect: 'manual' })

        if (response.type === 'opaqueredirect') {
            // CFZT is redirecting to its login page.
            // We can't follow cross-origin 302 from respondWith(),
            // so unregister the SW and reload to let the browser handle it.
            return new Response(
                `<!DOCTYPE html>
<html><head><meta charset="utf-8"><script>
navigator.serviceWorker.getRegistration().then(function(r){
if(r)r.unregister().then(function(){location.reload()});
else location.reload()});
</script></head><body>Redirecting to login...</body></html>`,
                { headers: { 'Content-Type': 'text/html' } }
            )
        }

        return response
    } catch {
        // Network error - serve cached index.html for offline/SPA support
        const cached = await matchPrecache('index.html')
        if (cached) return cached
        return new Response('Offline', {
            status: 503,
            headers: { 'Content-Type': 'text/plain' },
        })
    }
}

registerRoute(new NavigationRoute(navigationHandler))

// Step 3: Workbox plugin to prevent caching CFZT auth responses
const cfztCacheGuard = {
    cacheWillUpdate: async ({ response }: { response: Response }): Promise<Response | null> => {
        if (response.redirected && response.url.includes('cloudflareaccess.com')) {
            return null
        }
        const contentType = response.headers.get('content-type')
        if (contentType && contentType.includes('text/html')) {
            return null
        }
        return response
    },
}

// Step 4: API and streaming routes
registerRoute(
    ({ url }) => url.pathname.startsWith('/api/folders'),
    new NetworkFirst({
        cacheName: 'api-folders',
        plugins: [
            cfztCacheGuard,
            new ExpirationPlugin({
                maxEntries: 50,
                maxAgeSeconds: 60 * 60, // 1 hour
            }),
        ],
    })
)

registerRoute(
    ({ url }) => url.pathname.startsWith('/api/stream/'),
    new CacheFirst({
        cacheName: 'audio-cache',
        plugins: [
            cfztCacheGuard,
            new ExpirationPlugin({
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 1 week
            }),
            new RangeRequestsPlugin(),
        ],
    })
)

// Step 5: Add precache route for static assets (JS, CSS, images)
// Registered AFTER NavigationRoute so navigation requests hit our handler first
addRoute()
