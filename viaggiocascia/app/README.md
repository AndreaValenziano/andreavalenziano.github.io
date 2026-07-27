# Umbria 2026 — app di viaggio

PWA installabile e **completamente offline** per il viaggio in Umbria (Assisi, Cascia e la
Valnerina) del 9–12 agosto 2026. Mobile-first, in italiano, nessun backend: checklist, note e
spese restano in `localStorage` del telefono.

Stack: React + Vite + TypeScript · Tailwind CSS · `vite-plugin-pwa`.

## Comandi

```bash
cd viaggiocascia/app
npm install        # solo la prima volta
npm run dev        # sviluppo su http://localhost:5173/viaggiocascia/
npm run build      # typecheck + build di produzione in dist/
npm run preview    # serve la build per prova locale
npm run icons      # rigenera le icone PWA in public/ (serve solo se cambi il disegno)
npm run deploy     # build + copia della build in ../ (viaggiocascia/)
```

## Come modificare i contenuti del viaggio

Tutti i contenuti (giorni, tappe, ristoranti, parcheggi, orari, distanze, note, voci
precaricate della checklist) stanno in **due soli file dati**, mai dentro i componenti:

- `src/data/trip.ts` — l'itinerario completo, tipizzato (`Trip` in `src/types.ts`)
- `src/data/checklist.ts` — le voci precaricate della checklist

Regole:

- telefoni in formato E.164 nel campo `phone` (es. `+390743617003`) e versione leggibile in
  `phoneDisplay`;
- se un dato manca (telefono, coordinate…) **lascia il campo assente**: la UI nasconde da sola
  il pulsante corrispondente;
- dopo una modifica: `npm run deploy`, poi commit & push. I telefoni con l'app installata
  scaricano la nuova versione da soli alla prima apertura con rete (controllo orario + `autoUpdate`).

## Deploy su GitHub Pages

Questo repo è il **sito utente** `andreavalenziano.github.io`, pubblicato da GitHub Pages
direttamente dal branch `main` (root). L'app è quindi servita come sottocartella statica:
`https://andreavalenziano.github.io/viaggiocascia/`.

Per questo motivo **non** c'è un workflow GitHub Actions con `deploy-pages`: quel tipo di
deploy sostituirebbe l'intero sito (che contiene anche le altre web app del repo) con la sola
`dist/` di questa app. Il flusso è invece:

1. `npm run deploy` — builda e copia la build in `viaggiocascia/` (lo script
   `scripts/publish.mjs` rimuove solo gli artefatti di build noti, mai i sorgenti in `app/`
   né i file markdown);
2. `git add`, `git commit`, `git push` dal repo.

Non c'è nulla da attivare nelle impostazioni del repo: Pages è già configurato su
«Deploy from a branch». Il `base` di Vite è `/viaggiocascia/` (costante in cima a
`vite.config.ts`, sovrascrivibile con la variabile d'ambiente `VIAGGIO_BASE`); `start_url` e
`scope` del manifest PWA usano lo stesso valore.

## Installazione sui telefoni

**iPhone (Safari):** aprire l'URL → pulsante **Condividi** → **Aggiungi alla schermata Home**.

**Android (Chrome):** aprire l'URL → menu **⋮** → **Installa app** (o «Aggiungi a schermata Home»).

Dopo la prima apertura completa, l'app funziona **in modalità aereo**: il service worker
precarica app, dati, font e icone. L'unica funzione che richiede rete è «Portami lì»
(apertura delle mappe native). Le istruzioni sono ripetute anche dentro l'app, in
**Altro → Installare l'app**.

## Verifica dopo un deploy

- l'app si apre su `https://andreavalenziano.github.io/viaggiocascia/`;
- è installabile (vedi sopra);
- installata, funziona in modalità aereo;
- nessun 404 in console per icone/font.

## Struttura

```
app/
├── index.html
├── vite.config.ts        # base /viaggiocascia/, manifest PWA, precache workbox
├── public/               # icone generate (npm run icons)
├── scripts/
│   ├── generate-icons.mjs
│   └── publish.mjs       # copia dist/ → ../
└── src/
    ├── data/             # ⬅ contenuti del viaggio (unico posto da modificare)
    ├── lib/              # date Europe/Rome, link mappe, localStorage
    ├── components/       # UI condivisa (nav, azioni luogo, dialog, icone)
    └── tabs/             # le 5 schede: Giorni, Info, Checklist, Diario, Altro
```

## Dati mancanti da completare

Non inventati di proposito (la UI nasconde i pulsanti relativi): vedi l'elenco in fondo a
questo file dati — telefono dell'Hotel Delle Rose; telefoni di Trattoria Pallotta, Ristorante
San Francesco, La Locanda del Cardinale, La Taverna del Bordone e Ristorante Vespasia;
coordinate della Locanda Cacio Re e dei luoghi da visitare (per questi la mappa si apre con
la ricerca per nome + località, dati presenti nell'itinerario).
