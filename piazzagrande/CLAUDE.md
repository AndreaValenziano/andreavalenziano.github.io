# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`piazzagrande/` is a **book-digitization workspace**, not a web app: it turns the photographed book *piazza grande 2026|2027* (Azione Cattolica Italiana, Ave, 2026) into a structured Markdown file. Nothing here is served on the GitHub Pages site. The full plan, diagnostics and conventions live in `RUNBOOK_digitalizzazione.md` — read it before doing any pipeline work; this file only summarizes what you need to operate.

The book is copyrighted: digitization is for personal/service use, the resulting Markdown must not be redistributed.

## Files

- `PIAZZA GRANDE.pdf` — the source: 68 pages of iPhone photos (54 landscape double-page spreads + 14 portrait single pages ≈ 122 book pages), **~250 MB, no text layer** (OCR is mandatory). **Never read, render or `cat` this file wholesale** — it will blow the context. Extract single pages with `pdftoppm -f N -l N` or `pdftotext` on the OCR'd derivative instead. Not yet committed and should stay out of git (add it to the root `.gitignore`).
- `split_libro.py` — Stage 1 script: renders the PDF with `pdftoppm`, optionally rotates, splits each landscape spread into left/right single pages, keeps portrait pages as they are (`--skip auto`), re-saves as one PDF via Pillow.
- `RUNBOOK_digitalizzazione.md` — the operational briefing (Italian): material characteristics, OCR test results, the three-stage pipeline, and the `CONTESTO.md` template for cross-session state.

- `CONTESTO.md` — cross-session state: Markdown conventions, canonical glossary, progress. Read at the start and update at the end of every Stage 3 session.
- `mappa_pagine.txt` — original PDF page → `pagine/p-NNN.png` mapping.
- `spezza_ocr.py` — splits Marker's paginated output into `ocr/marker/pages/p-NNN.md`.
- `md/ISTRUZIONI_BLOCCO.md` — the Stage 3 brief given to each block agent; `md/blocco_A..H.md` — structured Markdown per block of ~15 photos (photo order).
- `assembla.py` — merges the blocks into **`piazza_grande_2026-2027.md`** (the deliverable) in printed-page order, inserting "page missing" comments and renaming footnotes to `[^pN-k]`. Re-run it after editing any block file; never edit the final file by hand.
- Generated, git-ignored: `rendered/` (raw 144 DPI renders of the 68 PDF pages), `pagine/` (122 split book pages), `singole.pdf`, `ocr/`, `.venv/`.

## Pipeline

**Stage 1 — geometric normalization** (`split_libro.py`):

```bash
python3 split_libro.py "PIAZZA GRANDE.pdf" singole.pdf --skip auto --rot 0 --dpi 144
```

- `--skip` — `auto` (portrait = single page) or a 1-based list. In this PDF the singles are 1, 2, 14, 19, 21, 22, 27, 28, 32, 35, 42, 43, 44, 53.
- `--rot` — **0 for this PDF** (spreads are already upright landscape); 90 = counter-clockwise, -90 = clockwise.
- `--offset` — shifts the cut line by % of width (-20..20) when the binding is off-centre; if it drifts across the volume, run in 2–3 blocks with different offsets.
- Always eyeball 4–5 pages (start / middle / end) before moving on: the cut must fall on the binding and no text line may be clipped.

Needs `pdftoppm` (poppler, installed) and Pillow (available system-wide and in `../esame/.venv`). ScanTailor Advanced between Stage 1 and 2 is optional but recommended for deskew/dewarp.

**Stage 2 — OCR to Markdown.** Two options, to be benchmarked on a 10-page mixed sample before running the whole volume:

- Marker — layout-aware, **chosen** after the benchmark (correct block order on post-it pages, recovers gutter-squeezed text). Installed in `.venv` (Python 3.13, needs `DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib` and `llama-server` from `brew install llama.cpp`; the current version has no `--languages` flag). ~20–25 s/page. Output: `ocr/marker/singole/singole.md` with `--paginate_output` page separators.
- Tesseract (`tesseract pagine/p-NNN.png out -l ita --psm 3`) — fast reference, output in `ocr/tesseract/`. Scrambles block order and garbles the first letters of lines near the binding.

Caveat: Surya's OCR is LLM-based and **invents plausible words where the photo is occluded** (binding curl): cross-check gutter passages against Tesseract and the page image in Stage 3.

**Stage 3 — Markdown structuring** (done 12 Sep 2026): 8 parallel agents, one per block, each starting from the Marker text, using Tesseract to cross-check and the page image only for lost titles, box attribution and gutter passages. Result: `md/blocco_*.md` → `assembla.py` → `piazza_grande_2026-2027.md` (~19.4k words, book pp. 1–125). Pages absent from the photos: 24, 34, 61, 94, 96, 104, 111 (96 and 104 are blank versos). Open doubts are listed in `CONTESTO.md` › Stato.

## Key facts about the source (from the runbook's diagnostics)

- Spreads in this export are already upright (landscape). If a future export has them rotated, rotate **before** cutting or you get useless half pages.
- PDF pages are sized 1 pt = 1 px of the photo, so native rendering is 72 DPI and effective text resolution only 110–150 DPI: render at 144 DPI, more gains nothing.
- Tesseract `-l ita --psm 3` is near-perfect on prose pages but scrambles reading order on magazine-style pages (coloured boxes, yellow post-its, round question boxes, handwritten signatures). **Layout, not OCR accuracy, is the real problem of this project.**

## Markdown conventions (decide once, then keep in `CONTESTO.md`)

Section titles = H2; quotes from the *Progetto formativo* = `>` blockquote + `(PF, p. N)`; yellow post-it questions = `> [!question]`; orange round boxes = `> [!tip]`; signatures = `*— Nome Cognome*, ruolo`; footnotes `[^n]` collected at chapter end; book page numbers as `<!-- p. N -->` HTML comments; original italics = `*…*`, small caps = `**…**`. The `[!question]`/`[!tip]` callout choice targets a knowledge base / full-text search; switch to `:::box` containers only if a re-typeset PDF or web page is the goal. `CONTESTO.md` must also hold the canonical spelling glossary (AC, Settore giovani, Équipe, Progetto formativo, …) and the "last block completed / last 3 lines / pending" state, and be updated at the end of every session.

Stage 3 output contract: return **only Markdown** — no preamble, comments or summaries.
