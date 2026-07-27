// Copia la build (dist/) nella cartella viaggiocascia/ del monorepo GitHub Pages.
// Rimuove solo gli artefatti di build noti: mai i sorgenti (app/) né i markdown.
// Uso: npm run deploy
import { cp, readdir, rm, stat } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const appDir = path.join(path.dirname(fileURLToPath(import.meta.url)), '..')
const distDir = path.join(appDir, 'dist')
const targetDir = path.resolve(appDir, '..')

try {
  await stat(distDir)
} catch {
  console.error('dist/ non trovata: esegui prima `npm run build`.')
  process.exit(1)
}

const knownArtifacts = [
  'index.html',
  'assets',
  'manifest.webmanifest',
  'sw.js',
  'sw.js.map',
  'registerSW.js',
  'favicon.svg',
  'apple-touch-icon.png',
  'pwa-192x192.png',
  'pwa-512x512.png',
  'maskable-icon-512x512.png',
]
const workboxFiles = (await readdir(targetDir)).filter((name) => /^workbox-.*\.js(\.map)?$/.test(name))

for (const name of [...knownArtifacts, ...workboxFiles]) {
  await rm(path.join(targetDir, name), { recursive: true, force: true })
}

await cp(distDir, targetDir, { recursive: true })
console.log(`Build pubblicata in ${targetDir}`)
console.log('Ora committa e pusha: il sito GitHub Pages servirà la nuova versione.')
