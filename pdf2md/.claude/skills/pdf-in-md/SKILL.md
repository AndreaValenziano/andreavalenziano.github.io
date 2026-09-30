---
name: pdf-in-md
description: Converte un PDF (dispense, sbobine, slide esportate, libri scansionati o fotografati) in un Markdown strutturato da usare come contesto per Claude, con le immagini descritte. Usare quando l'utente chiede di "convertire/trasformare un PDF in md", "preparare il materiale per Claude/per l'esame", "estrarre il testo da un PDF", "fare come per le sbobine di chimica" o porta un nuovo PDF da studiare.
---

# PDF → Markdown per Claude (pdf2md)

Gli strumenti stanno in `pdf2md/` alla radice della repo; si lanciano **dalla cartella del
documento** (es. `chimica/`), che l'utente sceglie (chiedere se non lo dice). Venv:
`pdf2md/.venv` (pymupdf4llm, Pillow). Se manca:
`export DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib; python3 -m venv pdf2md/.venv && pdf2md/.venv/bin/pip install -r pdf2md/requirements.txt`
(la variabile serve anche a ogni `pip` successivo: problema libexpat di macOS).

Principio: **tutto ciò che si può fare con uno script non costa token**. L'LLM serve solo per
ciò che uno script non può fare (descrivere immagini, rimettere in ordine un layout scansionato),
sempre con agenti in parallelo su lotti piccoli e con un file di istruzioni condiviso.

## 0. Ricognizione (sempre, pochi secondi)
```bash
pdfinfo "file.pdf"                                   # pagine, Creator/Producer (Word? scanner? iPhone?)
for p in 1 10 30 60; do pdftotext -f $p -l $p "file.pdf" - | wc -w; done   # c'è testo?
pdfimages -list "file.pdf" | tail -n +3 | wc -l      # quante immagini
```
- Decine/centinaia di parole per pagina → **strada digitale** (sezione 1).
- ~0 parole → **strada scansione** (sezione 2).
- Mai leggere il PDF intero con Read: al massimo `pdftoppm -f N -l N -r 60` su singole pagine.

## 1. Strada digitale (PDF con testo: Word, LaTeX, slide esportate)
Esempio completo: `chimica/` (*Sbobine 2*, 121 pagine, 207 immagini, ~15 minuti).

1. **Conversione** (0 token, ~20 s per 100 pagine):
   ```bash
   ../pdf2md/.venv/bin/python ../pdf2md/digitale.py "file.pdf" nome.raw.md
   ```
   → `nome.raw.md` con `<!-- p. N -->`, `img/pNNN-k.jpg` (ridotte a 1000 px, deduplicate, icone
   scartate), `immagini.tsv`.
2. **Controllo dei titoli** (pochi token): `grep -n "^#" nome.raw.md` e guardare solo quella
   lista. Cercare: livelli da rimappare (`--livelli 5:4`), falsi titoli (frasi, formule, testo
   finito dentro un'immagine), residui di intestazioni/piè di pagina (`grep -c "Nome Autore"`).
   Scrivere `titoli.tsv` (`<testo titolo senza markup>` TAB `<livello>`, 0 = testo normale).
3. **Descrizioni delle immagini** (unico passo con token veri):
   ```bash
   python3 ../pdf2md/descrizioni.py nome.raw.md --lotti 6     # ~35 immagini per lotto
   ```
   Lanciare **in un unico messaggio** un agente per lotto (Agent tool, `model: sonnet`,
   `run_in_background: true`) con il prompt:
   > Working directory: `<cartella documento>` (<di cosa parla il documento>). Read
   > `pdf2md/ISTRUZIONI_IMMAGINI.md` and follow it exactly for K=<k>: input
   > `descrizioni/lotto_<k>.md`, output `descrizioni/lotto_<k>.tsv`. Read every image listed
   > with the Read tool. Do not read other files.

   Poi verificare: `awk -F'\t' 'NF!=4 && $2!="decorativa"' descrizioni/lotto_*.tsv` deve essere vuoto
   e il numero di righe uguale alle immagini del lotto.
4. **Assemblaggio** (0 token, rilanciabile):
   ```bash
   python3 ../pdf2md/rifinisci.py nome.raw.md nome.md --rimuovi "Nome Autore" --livelli 5:4 \
       --titolo "Titolo" --descrizione "Da dove viene, cosa significano <!-- p. N --> e «Immagine:»"
   ```
   Non modificare a mano `nome.md`: correggere `titoli.tsv` o `descrizioni/lotto_*.tsv` e rilanciare.
5. **Verifiche**: `grep -c "<!-- p\."` = pagine; nessun `![](` senza alt; `grep "^#"` ha una
   gerarchia sensata; leggere 2-3 pagine a campione (inizio, metà, fine) confrontandole con
   `pdftotext -f N -l N`.

## 2. Strada scansione (PDF di foto o scansioni, senza testo)
La procedura completa, già usata per due libri, è in `guideac/.claude/skills/digitalizza-libro/SKILL.md`
e `guideac/CLAUDE.md`: taglio delle doppie pagine (`normalizza_scansioni.py` / `split_libro.py`),
OCR con Marker a blocchi (`ocr_marker.py`, `spezza_ocr.py`) e Tesseract come controllo,
strutturazione con ~8 agenti in parallelo, `assembla.py`. Gli stessi script sono copiati in
`pdf2md/`; per usarli da qui installare Marker nel venv (`pdf2md/.venv/bin/pip install marker-pdf`,
serve anche `brew install llama.cpp tesseract tesseract-lang`), perché `ocr_marker.py` cerca
`marker_single` nel venv accanto allo script.
Le immagini di contenuto (schemi, tabelle) si descrivono con lo stesso passo 3 della strada digitale.

## Git
Chiedere se il materiale va su git (il sito è pubblico). Se sì: PDF sorgente, `nome.md`, `img/`,
`titoli.tsv`, `descrizioni/lotto_*.tsv` (costano token: vanno conservati). Mai: `nome.raw.md`,
`immagini.tsv`, `descrizioni/lotto_*.md` (si rigenerano) — coperti da `.gitignore`.

## Consegna
Nel riepilogo: parole, titoli, immagini (contenuto/decorative), correzioni manuali fatte, dubbi
(immagini `[illeggibile]`, falsi titoli lasciati).
