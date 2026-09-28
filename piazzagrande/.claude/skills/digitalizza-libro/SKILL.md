---
name: digitalizza-libro
description: Digitalizza un libro fotografato o scansionato (PDF senza testo, anche misti tra scanner piano, foto di pagine singole e foto di doppie pagine) in pagine singole, un PDF ricercabile da condividere con una pagina per pagina e un Markdown strutturato. Usare quando l'utente chiede di "fare lo stesso lavoro di piazza grande", "digitalizzare/trascrivere un libro/guida/sussidio", "tagliare le doppie pagine", "fare l'OCR delle scansioni", "preparare il PDF delle pagine da condividere" o porta una nuova cartella di scansioni in piazzagrande/.
---

# Digitalizzazione di un libro (pipeline piazzagrande)

Tutti gli script stanno in `piazzagrande/` (questa cartella) e si lanciano **dalla cartella del
libro** (es. `piazzagrande/guida ac/`) con `../.venv/bin/python ../script.py`. Il venv ha
Pillow, numpy e Marker; servono anche `tesseract` (con `ita`), `pdftoppm`/`pdfunite` (poppler)
e `llama-server` (brew `llama.cpp`, usato da Marker).
Esempi completi già fatti: `piazzagrande/` (piazza grande, solo doppie pagine) e
`piazzagrande/guida ac/` (Wow che tratto 2: scanner piano + foto singole + doppie pagine).
Leggi `RUNBOOK_digitalizzazione.md` per il contesto tecnico.

Regole d'oro:
- **Mai** leggere o `cat` i PDF sorgente interi (centinaia di MB): lavorare su miniature
  (`pdftoppm -jpeg -scale-to 400`) e su singole pagine.
- Opere protette da copyright e sito pubblico: sorgenti, pagine, OCR e PDF vanno in
  `.gitignore` (vedi le righe già presenti per `guida ac`).
- Dire all'utente in poche parole a che punto si è: il lavoro dura 1-2 ore.

## 0. Ricognizione (sempre)
1. `pdfinfo` e `pdfimages -list -f 1 -l 3` su ogni PDF: pagine, dimensioni, `/Rotate`
   (pdftoppm la applica già), risoluzione (scanner 300 dpi; foto iPhone esportate da Quartz = 72 dpi nominali).
2. Fogli di miniature per ogni PDF (Pillow, 6 per riga) e guardarli: classificare ogni PDF come
   - `piana`: scanner piano, una pagina appoggiata nell'angolo in alto a sinistra dell'A4
   - `singola`: foto di una pagina già ritagliata
   - `doppia`: foto di doppie pagine (una pagina verticale dentro un PDF `doppia` è trattata come singola)
3. Annotare duplicati evidenti tra un PDF e l'altro (lo stesso foglio rifotografato).

## 1. Taglio delle pagine — `normalizza_scansioni.py`
```bash
../.venv/bin/python ../normalizza_scansioni.py pagine "src/1.pdf:piana" "src/3.pdf:singola" "src/4.pdf:doppia" \
    --anteprima anteprima_tagli.jpg
```
Produce `pagine/p-NNN.png` (ordine dei PDF) e `mappa_pagine.txt`. Richiede ~5 min per 90 fogli.
- Rilegatura delle doppie pagine: cercata come "valle" di luminosità continua nel 42-58% della larghezza.
  Correzioni manuali: `--tagli "4.pdf:5=0.53,6.pdf:4=0.51"` (frazione della larghezza).
- Scanner piano: finestra del piede `--piana-basso 0.645-0.70` (frazione dell'altezza A4), bordo destro
  `--piana-destra`, sinistro `--piana-sinistra`. Se la pagina del libro ha un'altra dimensione, adattarle.
- **Controllo visivo obbligatorio**: fogli di miniature di tutte le pagine tagliate (8 per riga).
  Segnali d'errore: testo tagliato al piede, un titolo spezzato a metà ("SEQUELA PERSONALIZZ"),
  una striscia larga dell'altra pagina. Per verificare un taglio, disegnare la linea sulla doppia
  pagina a bassa risoluzione e guardarla. Correggere e rilanciare (rigenera tutto).

## 2. Numeri di pagina stampati — `pagine_stampate.tsv`
Tesseract non legge i numeri nei cerchietti colorati: fare un foglio con gli angoli in basso
(sinistro e destro, ~13% × 16%) di ogni pagina e leggerli a vista. Scrivere
`pagine_stampate.tsv` (`p-NNN<TAB>pagina<TAB>nota`, `-` = duplicato da escludere; nell'intestazione
le pagine mancanti). Tra due duplicati tenere la versione più nitida (scanner piano > foto).

## 3. PDF da condividere — `pdf_condivisione.py`
```bash
cd .. && .venv/bin/python pdf_condivisione.py "cartella libro" "cartella libro/Titolo.pdf"
```
Ordine delle pagine stampate, senza duplicati, livello di testo OCR (tesseract `pdf`),
segnaposto "Pagina N non presente nelle scansioni" per le mancanti. ~1 min; ~45 MB per 130
pagine (`--lato 1500 --qualita 65` per alleggerire). Verificare con `pdfinfo` e `pdftotext -f 10 -l 10`.

## 4. OCR
- Tesseract (veloce, non inventa):
  `ls pagine/*.png | xargs -P 6 -I{} sh -c 'b=$(basename {} .png); tesseract {} ocr/tesseract/$b -l ita --psm 3 >/dev/null 2>&1'`
- Marker (layout corretto, ~30 s/pagina) su un PDF delle pagine tagliate in ordine di file:
  ```bash
  ../.venv/bin/python ../split_libro.py x singole.pdf --png pagine --reuse --dpi 150
  ../.venv/bin/python ../ocr_marker.py singole.pdf      # in background: ~1 h per 130 pagine
  ../.venv/bin/python ../spezza_ocr.py                   # -> ocr/marker/pages/p-NNN.md
  ```
  `ocr_marker.py` lavora a blocchi di 20 pagine con timeout e nuovi tentativi, perché il
  llama-server di Surya ogni tanto si blocca (0% CPU) e Marker in un colpo solo non finisce mai.
  È rilanciabile: salta i blocchi già fatti.

## 5. Strutturazione in Markdown (Stadio 3)
1. Scrivere `CONTESTO.md` nella cartella del libro (modello: `guida ac/CONTESTO.md`): struttura
   del volume dall'indice, convenzioni Markdown (gerarchia H1-H5, box, note, commenti di pagina),
   glossario con la grafia canonica, stato. Guardare 4-6 pagine tipo prima di fissare le convenzioni.
2. Copiare e adattare `guida ac/md/ISTRUZIONI_BLOCCO.md`.
3. Dividere le pagine (esclusi i duplicati) in ~8 blocchi di ~16 pagine, tagliando se possibile
   all'inizio di una sezione, e lanciare **in parallelo** un agente per blocco (Agent tool, in un
   unico messaggio) con: cartella, lettera del blocco, elenco `p-NNN → p. N`, e il rimando a
   `md/ISTRUZIONI_BLOCCO.md` e `CONTESTO.md`. Ogni agente scrive `md/blocco_X.md`.
   Non serve aspettare tutto Marker: `spezza_ocr.py ocr/marker/blocchi/AAAA-BBBB/singole/singole.md`
   estrae le pagine di un blocco appena finito, e l'agente che le usa può partire subito.
   Chiedere agli agenti di segnalare le righe con lettere perse vicino alla rilegatura: quasi
   sempre è un taglio troppo spostato (le lettere compaiono sul bordo della pagina accanto).
   Correggere con `--tagli`, rilanciare `normalizza_scansioni.py` e `pdf_condivisione.py`
   **solo dopo** che tutti gli agenti hanno finito (rigenera tutte le immagini).
4. Raccogliere i rapporti: unificare le proposte di glossario in `CONTESTO.md`, controllare
   la coerenza dei titoli tra i blocchi (grep di `^#`), correggere a mano i blocchi.
5. Assemblare (mai modificare a mano il file finale):
   ```bash
   ../.venv/bin/python ../assembla.py --titolo "Titolo — sottotitolo" --descrizione "Trascrizione …" --out nome_libro.md
   ```
   Verifica: nessuna pagina mancante inattesa nell'output di assembla, `grep -c "<!-- p\."`,
   nessun `<sup>` residuo, note `[^pN-k]` con definizione.
6. Aggiornare `CONTESTO.md` › Stato (pagine mancanti, dubbi) e il `CLAUDE.md` di piazzagrande
   se è cambiato qualcosa nella pipeline.

## Risultati da consegnare
- `pagine/` (una immagine per pagina), `pagine_stampate.tsv`
- PDF da condividere con una pagina per pagina, ricercabile
- Markdown finale strutturato + `CONTESTO.md` aggiornato
- Nel riepilogo: pagine mancanti/duplicate, tagli corretti a mano, dubbi aperti
