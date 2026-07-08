/* Service worker di "La mia dieta" — offline-first per la shell + i CDN,
   ma network-first per dieta.md (così le modifiche compaiono quando sei online). */

const VERSION = 'dieta-v1';

// Shell dell'app (stessa origine)
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-512-maskable.png',
  './apple-touch-icon.png',
  './favicon-32.png',
];

// Dipendenze da CDN (cross-origin): cachate come opache (no-cors)
const CDN = [
  'https://unpkg.com/react@18.3.1/umd/react.production.min.js',
  'https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js',
  'https://unpkg.com/@babel/standalone@7.25.6/babel.min.js',
  'https://cdn.tailwindcss.com',
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    await cache.addAll(SHELL);
    // best-effort: se un CDN non risponde non blocchiamo l'installazione
    await Promise.allSettled(CDN.map(async (url) => {
      try {
        const res = await fetch(url, { mode: 'no-cors' });
        await cache.put(url, res);
      } catch (_) { /* ignora */ }
    }));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // dieta.md -> network-first: prova la rete (dati freschi), fallback alla cache
  if (url.pathname.endsWith('dieta.md')) {
    event.respondWith((async () => {
      try {
        const res = await fetch(req, { cache: 'no-store' });
        const cache = await caches.open(VERSION);
        cache.put(req, res.clone());
        return res;
      } catch (_) {
        const cached = await caches.match(req);
        return cached || Response.error();
      }
    })());
    return;
  }

  // shell + CDN -> cache-first, poi rete (e memorizza per la prossima volta)
  event.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const res = await fetch(req);
      if (res && (res.ok || res.type === 'opaque')) {
        const cache = await caches.open(VERSION);
        cache.put(req, res.clone());
      }
      return res;
    } catch (_) {
      // navigazione offline senza cache: ripiega sulla home
      if (req.mode === 'navigate') return caches.match('./index.html');
      return Response.error();
    }
  })());
});
