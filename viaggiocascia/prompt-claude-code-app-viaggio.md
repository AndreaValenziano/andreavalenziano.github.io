# Prompt per Claude Code — App di viaggio "Umbria 2026"

> Da incollare in Claude Code **allegando anche il file `itinerario-umbria-2026.md`**.

---

Ciao, devo costruire una piccola web app per un viaggio che farò con la mia ragazza in Umbria dal 9 al 12 agosto 2026.

Ti allego il file `itinerario-umbria-2026.md`: **è la fonte di verità dei contenuti**. Leggilo per intero prima di iniziare.

## Obiettivo

Una **PWA installabile sullo smartphone che funzioni completamente offline**, in italiano, mobile-first, che ci accompagni durante il viaggio.

Il punto critico: in Valnerina e verso Roccaporena **il segnale è spesso assente**. L'app deve quindi essere utilizzabile al 100% senza rete, dopo la prima apertura. Nessuna chiamata di rete a runtime, nessuna dipendenza da CDN, font inclusi localmente.

## Stack richiesto

- **React + Vite + TypeScript**
- **Tailwind CSS**
- **`vite-plugin-pwa`** con service worker che precarica tutto l'app shell e gli asset
- **Nessun backend, nessun account, nessuna API key, nessun database.** Persistenza solo in `localStorage`
- Deve essere buildata in statico e pubblicata su **GitHub Pages** (vedi sezione dedicata più sotto)

## Architettura dei dati

Non mettere i contenuti dentro i componenti. Crea un **unico file di dati tipizzato** (`src/data/trip.ts` o `trip.json` + tipi TS) che contenga tutto l'itinerario, generato a partire dal markdown allegato. Deve essere facilmente modificabile da me in seguito senza toccare il codice.

Struttura suggerita (adattala se hai idee migliori):

```ts
type Trip = {
  title: string
  startDate: string      // "2026-08-09"
  endDate: string        // "2026-08-12"
  timezone: "Europe/Rome"
  accommodation: Place
  days: Day[]
  restaurants: Place[]
  parkings: Parking[]
  openingHours: OpeningHours[]
  practicalNotes: string[]
  toConfirm: string[]
  distances: { from: string; to: string; km: string; time: string }[]
}

type Day = {
  date: string           // "2026-08-09"
  weekday: string        // "Domenica"
  title: string
  subtitle?: string
  meals: { breakfast: string; lunch: string; dinner: string }
  timeline: Stop[]
  parkingNote?: string
  note?: string
}

type Stop = {
  time: string           // "~08:00" oppure "Mattina"
  title: string
  description: string
  placeRef?: string      // id di un Place
}

type Place = {
  id: string
  name: string
  category: "hotel" | "restaurant" | "sight" | "parking"
  address?: string
  phone?: string         // formato E.164 per il link tel:
  lat?: number
  lng?: number
  rating?: number
  notes?: string
  priceRange?: string
}
```

### ⚠️ Regola importante sui dati

**Non inventare nulla.** Numeri di telefono, indirizzi, orari e coordinate devono provenire dal markdown allegato o dai dati che ti fornisco qui sotto. Se un dato manca (es. coordinate di un luogo o telefono dell'hotel), lascia il campo `undefined` e gestisci l'assenza nella UI (niente pulsante mappa o niente pulsante telefono), **senza inventare valori plausibili**. Se serve, segnalami alla fine l'elenco dei dati mancanti da completare.

Coordinate e telefoni già verificati che puoi usare:

| Luogo | Lat | Lng | Telefono |
|---|---|---|---|
| Trattoria l'Appennino (Cascia) | 42.7156409 | 13.0139963 | +393888055527 |
| Trattoria Il Grottino da Orlando (Cascia) | 42.7176852 | 13.0134291 | +393347047014 |
| Osteria La Cascata (Marmore/Terni) | 42.5551880 | 12.7095499 | +390744080993 |
| Il Pavone d'Oro (Marmore/Terni) | 42.5562565 | 12.7176435 | +39074462148 |
| Locanda Cacio Re (Vallo di Nera) | — | — | +390743617003 |

## Funzionalità

### 1. Home / giorno corrente (la funzione chiave)

L'app deve **sincronizzarsi con la data reale** (fuso `Europe/Rome`) e mostrare direttamente il giorno di interesse:

- **Prima del 9 agosto** → schermata di countdown ("mancano X giorni") + accesso alla panoramica del viaggio
- **Dal 9 al 12 agosto** → apre **direttamente sul giorno corrente**, con evidenziata la tappa più vicina all'ora attuale
- **Dopo il 12 agosto** → modalità "archivio", navigazione libera fra i giorni

In ogni caso deve sempre essere possibile **navigare manualmente** agli altri giorni (tab o swipe fra 9 · 10 · 11 · 12), senza restare bloccati sul giorno odierno.

### 2. Vista giorno

Timeline verticale delle tappe con orario, titolo, descrizione. Per ogni tappa collegata a un luogo, mostra i pulsanti azione:

- **📞 Chiama** → link `tel:` con il numero in formato E.164
- **🧭 Portami lì** → apertura della mappa nativa. Usa un link universale che funzioni sia su iOS che Android, con le coordinate quando disponibili e fallback sull'indirizzo testuale. **Attenzione: questo è l'unico punto in cui è accettabile che serva la rete** — l'app in sé deve restare consultabile offline.

In cima al giorno mostra il riepilogo pasti (colazione / pranzo / cena) evidenziando quali sono inclusi in mezza pensione e quali vanno organizzati fuori.

Il **martedì 11 agosto è il nostro anniversario**: dev'essere visivamente distinto dagli altri giorni (accento speciale, senza esagerare).

### 3. Sezioni trasversali

Schede/tab dedicate, tutte consultabili offline:

- **Hotel** — Hotel Delle Rose, con telefono, indirizzo, mappa, nota sul parcheggio gratuito e sulla mezza pensione
- **Ristoranti** — elenco con giorno di riferimento, telefono, mappa, fascia di prezzo
- **Parcheggi** — il riepilogo del markdown, con avviso ben visibile sulla **ZTL di Assisi**
- **Orari dei luoghi** — con etichetta chiara "da riverificare prima della partenza"
- **Distanze e tempi** — la tabella degli spostamenti
- **Note pratiche** e **Da confermare** — la checklist delle cose da verificare/prenotare

### 4. Checklist (con persistenza)

Checklist a spunta salvate in `localStorage`, divise per categorie:

- Valigia
- Prenotazioni da fare (es. cena Locanda Cacio Re + tavolo in terrazza, early check-in, conferma mezza pensione spostata a pranzo l'11)
- Cose da non dimenticare

Deve essere possibile **aggiungere, modificare ed eliminare voci**, non solo spuntare quelle predefinite. Precarica le voci ricavabili dalla sezione "Da confermare" del markdown.

### 5. Note e spese

- **Note libere** per giorno, salvate in `localStorage`
- **Spese**: aggiunta rapida di una voce (descrizione, importo, giorno, categoria opzionale), con **totale complessivo e totale per giorno**. Valuta in euro
- Deve funzionare offline e sopravvivere alla chiusura dell'app

### 6. Import / export dei dati personali

Poiché io e la mia ragazza avremo **ognuno la propria copia indipendente** (nessuna sincronizzazione), aggiungi un piccolo pannello impostazioni con:

- **Esporta** i dati utente (checklist, note, spese) in un file JSON
- **Importa** da file JSON
- **Reset** dei dati utente, con conferma

Questo serve anche come backup, dato che `localStorage` può essere cancellato.

## Design

Mobile-first, pensato per essere usato **all'aperto e in pieno sole**:

- Contrasto alto, testo generoso, aree touch ampie (min 44px)
- Palette calda ispirata all'Umbria (pietra, terracotta, verde salvia, oro), non il solito tema blu di default
- Tipografia curata e leggibile, font caricati localmente
- Micro-animazioni discrete, niente effetti pesanti
- **Dark mode** apprezzata (utile la sera)
- Deve essere gradevole: sarà usata in un viaggio speciale, non è un gestionale

## Requisiti PWA

- `manifest.json` completo con nome, icone (tutte le dimensioni necessarie), `display: standalone`, theme color coerente con la palette
- Service worker che precarica app shell, dati, font e icone
- **Verifica esplicitamente** che dopo la prima visita l'app si apra e funzioni in modalità aereo
- Includi nel README le **istruzioni di installazione su iPhone** (Safari → Condividi → Aggiungi a Home) **e su Android** (Chrome → Installa app), perché la useremo entrambi

## Deploy su GitHub Pages

Il sito sarà pubblicato su **GitHub Pages**. Questo ha conseguenze precise sulla configurazione: tienine conto fin dall'inizio, non come aggiustamento finale.

### Base path

Il sito starà in un sottopercorso del tipo `https://<utente>.github.io/<nome-repo>/`. Di conseguenza:

- In `vite.config.ts` imposta `base: '/<nome-repo>/'` (rendilo facilmente modificabile, es. tramite variabile in cima al file o env, così se cambio nome al repo non devo cercarlo)
- Nel `manifest.json` della PWA, **`start_url` e `scope` devono includere lo stesso base path**, altrimenti l'app installata si apre su una pagina bianca
- Passa il `base` anche a `vite-plugin-pwa`
- **Nessun path assoluto hardcoded** per icone, font o asset: tutto deve passare dal base path di Vite. Questo è l'errore che rompe più spesso le PWA su GitHub Pages

### Routing

GitHub Pages non gestisce i rewrite lato server: ricaricando una rotta tipo `/giorno/10` si ottiene un 404.

Scegli **una** di queste soluzioni e dimmi quale hai usato:

1. **Nessun router**: navigazione a tab gestita con lo stato React (è la mia preferita per un'app così piccola — semplice e senza sorprese)
2. **`HashRouter`** di React Router (URL con `#`, sempre sicuri su Pages)
3. `BrowserRouter` + copia di `index.html` in `404.html` durante la build

Evita `BrowserRouter` senza fallback: si rompe al refresh.

### Workflow di deploy

Crea un workflow GitHub Actions (`.github/workflows/deploy.yml`) che a ogni push sul branch principale:

1. fa il checkout, installa le dipendenze e builda
2. pubblica la cartella `dist/` con le action ufficiali (`actions/upload-pages-artifact` + `actions/deploy-pages`)
3. usa i permessi corretti (`pages: write`, `id-token: write`)

Nel README spiegami anche cosa devo attivare a mano una tantum nelle impostazioni del repo (Settings → Pages → Source: GitHub Actions).

### Service worker e aggiornamenti

- GitHub Pages serve in HTTPS, quindi il service worker funziona senza problemi
- Configura una **strategia di aggiornamento chiara**: quando pubblico una nuova versione dei dati (es. cambio un orario), l'app installata sui telefoni deve accorgersene. Usa `registerType: 'autoUpdate'` oppure mostra un piccolo avviso "Nuova versione disponibile — aggiorna"
- Questo è importante: modificherò i contenuti nei giorni prima della partenza e devono arrivare su entrambi i telefoni

### Verifica finale

Prima di considerare il lavoro concluso, controlla che dopo il deploy:

- l'app si apra correttamente all'URL con sottopercorso
- sia installabile ("Aggiungi a Home" su iOS, "Installa app" su Android)
- una volta installata, **funzioni in modalità aereo**
- icone e font si carichino (nessun 404 in console)

## Consegna

1. Progetto completo e funzionante, con `npm install` + `npm run dev` + `npm run build` che girano senza errori
2. `README.md` con: come avviare, come buildare, **come modificare i contenuti del viaggio** (dove sta il file dati e come cambiarlo), come installare la PWA sui telefoni
3. Codice pulito e componenti separati, così posso metterci mano dopo
4. Alla fine, elencami: (a) i dati mancanti che devo completare, (b) le eventuali scelte che hai fatto al posto mio

## Cosa NON fare

- Nessun backend, login, account o servizio esterno
- Nessuna chiave API
- Nessuna libreria di mappe pesante da renderizzare (bastano i link alle mappe native)
- Non inventare dati non presenti nel markdown o nella tabella qui sopra
- Non lasciare testo segnaposto tipo "Lorem ipsum" o "TODO" nella UI finale

Se qualcosa non è chiaro o hai bisogno di decisioni da parte mia, chiedimelo prima di iniziare a scrivere codice.
