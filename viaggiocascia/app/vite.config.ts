import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// Base path del deploy: l'app vive in un sottopercorso di andreavalenziano.github.io.
// Se il percorso cambia, basta aggiornare questa costante (o esportare VIAGGIO_BASE).
const BASE = process.env.VIAGGIO_BASE ?? '/viaggiocascia/'

export default defineConfig({
  base: BASE,
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        id: BASE,
        name: 'Umbria 2026 — Assisi, Cascia e la Valnerina',
        short_name: 'Umbria 2026',
        description:
          'Itinerario, checklist, note e spese del viaggio in Umbria (9–12 agosto 2026). Funziona completamente offline.',
        lang: 'it',
        dir: 'ltr',
        start_url: BASE,
        scope: BASE,
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#f6f0e6',
        theme_color: '#b4512e',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'maskable-icon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2,webmanifest}'],
        navigateFallback: `${BASE}index.html`,
      },
    }),
  ],
})
