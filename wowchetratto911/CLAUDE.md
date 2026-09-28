# CLAUDE.md — wowchetratto911

Webapp statica (vanilla JS, nessun build step lato front-end) per consultare le **attività** della guida
Acr 9-11 *Wow, che tratto! 2* (2026-2027), pubblicata su GitHub Pages in `/wowchetratto911/`.

## Copyright: contenuti cifrati
La guida è protetta da copyright e il sito è pubblico: nel repository va **solo `dati.enc`** (AES-256-GCM,
chiave PBKDF2-SHA256 dalla password). `fonte/` (Markdown della guida, `dati.json` in chiaro) è git-ignorata.
Mai committare testo della guida in chiaro in questa cartella.

## File
- `fonte/wow_che_tratto_2.md`, `fonte/CONTESTO.md` — copie da `guideac/9-11/` (convenzioni Markdown in CONTESTO.md)
- `tools/build.py` — Markdown → JSON (anno, fasi, attività con HTML già renderizzato) → `dati.enc`. Richiede `cryptography`.
- `index.html`, `style.css`, `app.js` — app (routing a hash: `#/`, `#/a/<id>`, `#/fasi[/n]`, `#/anno`, `#/salvate`)
- `img/` — logo WOW e logo Ac per la testata (originali in `materiale/`); `icon-*.png`, `favicon.png` generati dal logo WOW
- `sw.js`, `manifest.webmanifest` — PWA offline; alzare `VERSIONE` in `sw.js` se cambia l'elenco dei file

## Rigenerare i dati
```bash
cd wowchetratto911
python3 tools/build.py                          # chiede la password (min. 8 caratteri)
python3 tools/build.py --chiaro fonte/dati.json --solo-chiaro   # debug, senza cifrare
```
Cambiare password = rigenerare `dati.enc` (nuovo salt: i dispositivi che la ricordavano la richiedono).

## Modello dei dati (estratto da build.py)
- Seconda parte: H2 = fase; H3 = blocco (Liturgia, Carità, Catechesi, Verifica, Tempo Estate).
- Catechesi/Carità/Estate: H4 = tappa (Analisi, Confronto…, Studio, Animazione, Servizio), H5 = attività;
  la riga in corsivo sotto la tappa diventa `scopo`; "Suggerimenti per l'educatore" si accoda all'attività precedente;
  "Appunti per la festa…" e "Campo scuola" sono una scheda unica. Liturgia: una scheda per H4 (tempo/focus).
- Prima parte: solo le sezioni elencate in `ANNO_TENUTE`.

## Aspetto
Palette presa dalla copertina (pesca, rosso Acr, blu e giallo del WOW), token in `:root` di `style.css`. Tema chiaro predefinito; la modalità notte si attiva col pulsante ☾ (`data-theme="dark"`, salvata in `wct.tema`). "Carità" si mostra come "Carità (attività)" (`etichetta()` in app.js): lì stanno le attività per i ragazzi.

## Stato locale (localStorage, per dispositivo)
`wct.chiave` (chiave AES esportata se "Ricorda"), `wct.stato` (salvate, fatte, appunti, spunte delle verifiche), `wct.filtri`, `wct.tema`.
