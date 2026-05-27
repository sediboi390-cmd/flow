/**
 * coop-sw.js — Service Worker that injects COOP/COEP headers
 * Required for FFmpeg.wasm to use SharedArrayBuffer on GitHub Pages.
 *
 * How it works:
 *   Every fetch response is cloned and re-sent with the two headers that
 *   unlock SharedArrayBuffer in the browser:
 *     - Cross-Origin-Opener-Policy: same-origin
 *     - Cross-Origin-Embedder-Policy: require-corp
 */

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

self.addEventListener('fetch', e => {
  // Only handle GET requests
  if (e.request.method !== 'GET') return;

  e.respondWith(
    fetch(e.request)
      .then(response => {
        // Clone headers and inject COOP/COEP
        const headers = new Headers(response.headers);
        headers.set('Cross-Origin-Opener-Policy', 'same-origin');
        headers.set('Cross-Origin-Embedder-Policy', 'require-corp');

        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers
        });
      })
      .catch(() => fetch(e.request)) // fallback: pass through on error
  );
});
