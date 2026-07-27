// Genera le icone PWA (paesaggio umbro: sole d'oro su colline di salvia)
// a partire da un unico SVG. Uso: npm run icons
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const publicDir = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public')

// scale < 1 restringe il disegno sullo sfondo pieno (zona sicura delle icone maskable)
function iconSvg(scale = 1) {
  const size = 512
  const offset = (size * (1 - scale)) / 2
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#d9714a"/>
      <stop offset="1" stop-color="#b4512e"/>
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" fill="url(#sky)"/>
  <g transform="translate(${offset} ${offset}) scale(${scale})">
    <circle cx="256" cy="192" r="86" fill="#f3d98b"/>
    <path d="M-20 330 C 110 236, 240 258, 322 330 C 396 394, 470 380, 532 342 L 532 532 L -20 532 Z" fill="#8a9b73"/>
    <path d="M-20 402 C 100 340, 260 348, 380 420 C 442 454, 500 442, 532 424 L 532 532 L -20 532 Z" fill="#566546"/>
  </g>
</svg>`
}

await mkdir(publicDir, { recursive: true })
await writeFile(path.join(publicDir, 'favicon.svg'), iconSvg())

const outputs = [
  { file: 'pwa-192x192.png', size: 192, svg: iconSvg() },
  { file: 'pwa-512x512.png', size: 512, svg: iconSvg() },
  { file: 'maskable-icon-512x512.png', size: 512, svg: iconSvg(0.78) },
  { file: 'apple-touch-icon.png', size: 180, svg: iconSvg() },
]

for (const { file, size, svg } of outputs) {
  await sharp(Buffer.from(svg)).resize(size, size).png().toFile(path.join(publicDir, file))
  console.log('✓', file)
}
