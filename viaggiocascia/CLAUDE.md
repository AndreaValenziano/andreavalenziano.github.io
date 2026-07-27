# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`viaggiocascia/` hosts an Italian-language, offline-first PWA for a trip to Umbria (Assisi, Cascia, Valnerina) on 9–12 August 2026, served at `https://andreavalenziano.github.io/viaggiocascia/`. The folder contains **both the source and the committed build output**:

- `app/` — the Vite project (React 19 + TypeScript + Tailwind CSS v4 + `vite-plugin-pwa`). See `app/README.md` for full usage docs.
- `index.html`, `assets/`, `sw.js`, `workbox-*.js`, `manifest.webmanifest`, icons — **build artifacts** copied here by `npm run deploy`. Never edit these by hand; they are regenerated on every deploy.
- `itinerario-umbria-2026.md` — the original trip itinerary, source of truth for app content.
- `prompt-claude-code-app-viaggio.md` — the original build spec (stack, features, PWA/deploy requirements).

## Commands

```bash
cd viaggiocascia/app
npm install      # first time only
npm run dev      # dev server at http://localhost:5173/viaggiocascia/
npm run build    # tsc --noEmit + vite build → dist/
npm run preview  # serve the production build locally
npm run icons    # regenerate PWA icons in public/ (only if the artwork changes)
npm run deploy   # build + copy dist/ into ../ (viaggiocascia/), then commit & push
```

There are no tests; `npm run build` (which typechecks) is the verification gate, plus manual checks (installability, airplane-mode operation).

## Architecture

- **All trip content lives in `app/src/data/trip.ts`** (typed by `app/src/types.ts`) and `app/src/data/checklist.ts` (preloaded checklist items) — never inside components. Content edits go there, then `npm run deploy`.
- **Never invent data**: phone numbers (E.164 in `phone`, readable in `phoneDisplay`), coordinates, and hours must come from the itinerary markdown or user-verified sources. Missing fields stay `undefined`; the UI hides the corresponding button (`PlaceActions` renders Chiama/Portami lì only when data exists).
- No router: 5 tabs via React state (`App.tsx` + `components/BottomNav.tsx`) — Giorni, Info, Checklist, Diario (spese+note), Altro (tema, export/import/reset, install instructions).
- Date logic is timezone-pinned to Europe/Rome (`lib/dates.ts`): before 9 Aug → countdown/overview; during the trip → auto-opens current day with nearest stop highlighted; after → archive. Day 11 (`isAnniversary`) gets gold accents.
- User data (checklist, notes, expenses, theme) is in `localStorage` under `viaggiocascia.v1.*` (`lib/storage.ts`), with JSON export/import/reset — the two travelers have independent copies, no sync.
- 100% offline after first load: fonts via `@fontsource-variable` (bundled), no CDN, no runtime network calls. Only "Portami lì" opens native map links (`lib/maps.ts`: Apple Maps on iOS, Google Maps elsewhere).

## Deploy (important: no GitHub Actions)

This repo is the **user Pages site** deployed from branch `main` root, so an Actions `deploy-pages` workflow would replace the whole site with this app alone. Instead `app/scripts/publish.mjs` copies `dist/` into `viaggiocascia/` (removing only known build artifacts, never `app/` or the markdown files) and the build is committed. Keep `base: '/viaggiocascia/'` in `vite.config.ts` in sync with manifest `start_url`/`scope` (both derive from the `BASE` constant). SW is `registerType: 'autoUpdate'` + hourly update check, so content edits pushed before departure reach installed phones automatically.
