/* Service worker: l'app funziona offline dopo la prima apertura.
   Guscio e dati: stale-while-revalidate (si aggiornano alla visita successiva).
   Aumentare VERSIONE quando cambia l'elenco dei file del guscio. */
const VERSIONE = "wct-v2";
const GUSCIO = ["./", "index.html", "style.css", "app.js", "dati.enc", "manifest.webmanifest", "favicon.png", "img/wow.png", "img/logoac.png", "icon-192.png", "icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSIONE).then(c => c.addAll(GUSCIO)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(chiavi => Promise.all(chiavi.filter(k => k.startsWith("wct-") && k !== VERSIONE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const font = url.hostname.endsWith("fonts.googleapis.com") || url.hostname.endsWith("fonts.gstatic.com");
  if (url.origin !== location.origin && !font) return;
  e.respondWith(caches.open(VERSIONE).then(async cache => {
    const chiave = url.origin === location.origin ? url.pathname : req;
    const inCache = await cache.match(chiave, { ignoreSearch: true });
    const rete = fetch(req).then(r => {
      if (r.ok || r.type === "opaque") cache.put(chiave, r.clone());
      return r;
    }).catch(() => inCache);
    if (font && inCache) return inCache;
    return inCache ? (e.waitUntil(rete), inCache) : rete;
  }));
});
