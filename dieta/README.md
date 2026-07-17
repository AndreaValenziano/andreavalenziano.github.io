# La mia dieta

App web mobile-first per consultare la dieta settimanale e sfogliare le
alternative di ogni pasto. Italiano, singola pagina, nessuno step di build.

- **Fonte dati unica:** `dieta.md`. L'app lo legge e lo parsa **a runtime**:
  modifichi `dieta.md`, ricarichi la pagina e l'app è aggiornata — non si
  tocca `index.html`.
- **Stack:** React 18 + Tailwind (Play CDN) + Babel standalone. Le icone sono
  un piccolo sottoinsieme di [lucide](https://lucide.dev) inline (nessuna
  libreria pesante). Le scelte del giorno vivono solo nello stato React in
  memoria (niente `localStorage`): si azzerano al refresh.

## Avvio in locale

L'app usa `fetch('dieta.md')`, che **non funziona** aprendo il file con
`file://`. Serve un piccolo server statico. Dalla cartella `dieta/`:

```bash
python3 -m http.server 8000
```

poi apri <http://localhost:8000>. In alternativa: `npx serve` (Node).

In produzione su GitHub Pages funziona senza altro: è già servito via HTTP.

## Come è organizzato `dieta.md`

```markdown
## Lunedì                ← un GIORNO (Lunedì … Domenica)

### Pranzo               ← un PASTO del giorno

- **Carboidrato — proposta:** 30g (crudo) / 60g (cotto) Riso   ← voce INTERCAMBIABILE (proposta del giorno)
  - 30g Pasta di semola                                        ← ALTERNATIVA (2 spazi di indentazione)
  - 40g Pasta integrale
- 5g Olio (1 cucchiaino)                                       ← voce FISSA (vale sempre)
```

Regole del parser:

- `## <Giorno>` apre un giorno. Sono riconosciuti solo i nomi
  `Lunedì, Martedì, Mercoledì, Giovedì, Venerdì, Sabato, Domenica`; qualunque
  altro `##` (es. `## Come è strutturato`) viene ignorato.
- `### <Pasto>` apre un pasto (Colazione, Spuntino (mattina), Pranzo,
  Spuntino (pomeriggio), Cena — il nome è libero, l'icona si adatta).
- Bullet `- **Categoria — proposta:** valore` → **voce intercambiabile**. I
  bullet **indentati di 2 spazi** subito sotto sono le sue **alternative**.
  La categoria è testo libero (Carboidrato, Proteine, Latticino, Biscotti,
  Frutta secca, …).
- Qualsiasi altro bullet `- ...` a inizio riga → **voce fissa**.
- I promemoria idratazione vengono estratti dal blocco
  **Promemoria idratazione** dell'introduzione e mostrati nella nota fissa
  (icona goccia in alto a destra).
- Vengono **ignorati**: l'intro "Come è strutturato", i blockquote (`>`) e il
  marcatore `⚠️` (nota personale, rimosso dal testo mostrato).

Il parser tollera spazi/tab in più, righe vuote e i trattini `—`, `–`, `-`.

## Come aggiungere / modificare

**Un giorno:** aggiungi un blocco `## <Giorno>` (uno dei sette nomi) e sotto i
suoi `### Pasto`.

**Un pasto:** sotto un giorno aggiungi `### <Nome pasto>` e i suoi bullet.

**Una voce intercambiabile:**

```markdown
- **Proteine — proposta:** 156g Merluzzo
  - 65g Tonno sott'olio ben sgocciolato
  - 105g Salmone affumicato
```

**Un'alternativa a una voce esistente:** aggiungi un bullet indentato di
2 spazi sotto la sua riga `**… — proposta:**`.

**Una voce fissa:** un normale bullet `- ...` a inizio riga (nessun figlio),
es. `- 10g Olio (1 cucchiaio)`.

Non serve toccare `index.html`.

## Funzionalità

- Selettore dei 7 giorni (default = oggi), fascia scorrevole.
- Proposta del giorno in evidenza per ogni voce intercambiabile; tap per
  espandere le alternative e sceglierne una. La voce mostra la scelta con un
  badge "scelta" e un pulsante per tornare alla proposta originale.
- Voci fisse sempre visibili sotto le intercambiabili del pasto.
- Grammature/quantità evidenziate.
- Ricerca alimento tra tutte le voci (proposte, alternative, fisse): mostra
  in quali giorno/pasto compare; tap su un risultato porta a quel giorno.
- Pulsante **"Azzera scelte (N)"** accanto al titolo del giorno: riporta tutte
  le voci di quel giorno alle proposte originali (compare solo se hai fatto
  almeno una scelta).
- Nota fissa con i promemoria idratazione.

## PWA (installabile + offline)

L'app è una PWA: puoi installarla in home screen e usarla offline.

- `manifest.webmanifest` — nome, colori, icone (`icon-192.png`,
  `icon-512.png`, `icon-512-maskable.png`, `apple-touch-icon.png`). Le icone
  sono generate come PNG (foglia bianca su verde).
- `sw.js` — service worker. Strategia:
  - **shell + CDN** (React, Babel, Tailwind): *cache-first*, così l'app parte
    anche offline;
  - **`dieta.md`**: *network-first* (quando sei online scarica sempre l'ultima
    versione e la memorizza; offline usa l'ultima in cache).

Il service worker si attiva solo via `http(s)` (non con `file://`) — quindi in
locale usa il server statico, e su GitHub Pages funziona da subito.

Dopo aver modificato `dieta.md`, apri l'app online almeno una volta per far
aggiornare la copia in cache. Se cambi `index.html`/`sw.js`, incrementa
`VERSION` in `sw.js` per invalidare la vecchia cache.
