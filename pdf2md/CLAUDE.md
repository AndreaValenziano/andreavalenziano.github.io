# CLAUDE.md

`pdf2md/` raccoglie gli strumenti che trasformano un PDF in un Markdown strutturato da usare come
contesto per Claude (ripasso, domande d'esame, ricerca). Non è servito sul sito. La procedura
completa è nella skill `pdf-in-md` (`.claude/skills/pdf-in-md/SKILL.md`): leggerla prima di
convertire un nuovo PDF.

Gli script si lanciano **dalla cartella del documento** (es. `chimica/`), non da qui:
`../pdf2md/.venv/bin/python ../pdf2md/<script>.py`. Venv: `.venv/` (Python 3.14, `requirements.txt`;
su questo Mac creare venv con `DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib`).

## Strada digitale (PDF con testo)
- `digitale.py` — pymupdf4llm (titoli dalla dimensione del font, grassetti, elenchi, tabelle,
  intestazioni/piè di pagina tolti, OCR spento) → `<nome>.raw.md` con `<!-- p. N -->`; immagini in
  `img/pNNN-k.jpg` (JPEG, lato ≤ 1000 px, deduplicate per hash, icone < 60 px scartate) e `immagini.tsv`.
- `descrizioni.py` — divide le immagini uniche in lotti `descrizioni/lotto_K.md` con il testo attorno.
- `ISTRUZIONI_IMMAGINI.md` — brief per gli agenti (uno per lotto, in parallelo) che scrivono
  `descrizioni/lotto_K.tsv` (`file`, `contenuto|decorativa`, alt text, descrizione su una riga).
- `rifinisci.py` — `--rimuovi`, `--livelli`, `titoli.tsv` del documento, descrizioni come
  `> **Immagine:** …` sotto ogni immagine, intestazione → `<nome>.md`. Deterministico e rilanciabile.

## Strada scansione (PDF senza testo)
Copie degli script di `guideac/` (che resta invariato e ha la documentazione completa):
`split_libro.py`, `normalizza_scansioni.py`, `ocr_marker.py`, `spezza_ocr.py`,
`pdf_condivisione.py`, `assembla.py`. Marker non è installato in questo venv (vedi la skill).

## Documenti convertiti
- `../chimica/` — *Elementi di didattica della chimica*, sbobine (Word → PDF, 121 pp., 207 immagini).
