# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`guideac/` is a **book-digitization workspace** for Azione Cattolica guides, not a web app: it turns photographed/scanned books into single-page images, a searchable shareable PDF and a structured Markdown file. Nothing here is served on the GitHub Pages site. The books are copyrighted: digitization is for personal/service use, the resulting files must not be redistributed.

Layout: shared scripts, `.venv/` and the `digitalizza-libro` skill at the root; one subfolder per book, where every command is run from (`../.venv/bin/python ../script.py`).

- `piazza grande/` — *piazza grande 2026|2027* (Ave, 2026), photos of double-page spreads. The full plan, diagnostics and conventions live in `piazza grande/RUNBOOK_digitalizzazione.md` — read it before doing any pipeline work.
- `9-11/` — *Wow, che tratto! 2* (guida educatore Acr 9-11, 2026), from mixed sources (flatbed scans, single-page photos, double-page photos): see `9-11/CONTESTO.md`. Deliverables: `wow_che_tratto_2.md` and the shareable searchable PDF `Wow che tratto 2 - guida per l'educatore.pdf`.

## Files

Shared, book-agnostic scripts (root):
- `split_libro.py` — Stage 1 for spread-only PDFs: renders with `pdftoppm`, optionally rotates, splits each landscape spread into left/right pages, keeps portrait pages (`--skip auto`), re-saves as one PDF via Pillow.
- `normalizza_scansioni.py` — Stage 1 for mixed PDFs (`file.pdf:piana|singola|doppia`), gutter detection, manual overrides `--tagli`, `--anteprima` control sheet.
- `ocr_marker.py` — Marker in 20-page chunks with timeout/retry (the Surya llama-server sometimes hangs at 0% CPU).
- `spezza_ocr.py` — splits Marker's paginated output into `ocr/marker/pages/p-NNN.md`.
- `pdf_condivisione.py` — one-page-per-page PDF in printed order from `pagine_stampate.tsv`, with OCR text layer and placeholders for missing pages.
- `assembla.py --titolo … --descrizione … --out …` — merges `md/blocco_*.md` into the deliverable in printed-page order, inserting "page missing" comments and renaming footnotes to `[^pN-k]` (defaults = piazza grande). Re-run it after editing any block file; never edit the final file by hand.

Per book folder:
- the source PDF(s) — **hundreds of MB, no text layer**. **Never read, render or `cat` them wholesale**: extract single pages with `pdftoppm -f N -l N`. In `piazza grande/`: `piazza grande.pdf` (68 iPhone photos: 54 spreads + 14 portrait singles ≈ 122 book pages).
- `CONTESTO.md` — cross-session state: Markdown conventions, canonical glossary, progress. Read at the start and update at the end of every Stage 3 session.
- `mappa_pagine.txt` — source PDF page → `pagine/p-NNN.png` mapping.
- `md/ISTRUZIONI_BLOCCO.md` — the Stage 3 brief given to each block agent; `md/blocco_A..H.md` — structured Markdown per block.
- the Markdown deliverable (`piazza_grande_2026-2027.md`, `wow_che_tratto_2.md`).
- Generated, git-ignored (see root `.gitignore`, `guideac/*/…`): all PDFs, `rendered/`, `pagine/`, `ocr/`, `scansione originali/`, `anteprima_tagli.jpg`; plus `guideac/.venv/`.

The project skill `digitalizza-libro` (`.claude/skills/`) describes the whole procedure for a new book: create a new subfolder here.

## Pipeline

**Stage 1 — geometric normalization** (`split_libro.py`, piazza grande):

```bash
cd "piazza grande" && python3 ../split_libro.py "piazza grande.pdf" singole.pdf --skip auto --rot 0 --dpi 144
```

- `--skip` — `auto` (portrait = single page) or a 1-based list. In this PDF the singles are 1, 2, 14, 19, 21, 22, 27, 28, 32, 35, 42, 43, 44, 53.
- `--rot` — **0 for this PDF** (spreads are already upright landscape); 90 = counter-clockwise, -90 = clockwise.
- `--offset` — shifts the cut line by % of width (-20..20) when the binding is off-centre; if it drifts across the volume, run in 2–3 blocks with different offsets.
- Always eyeball 4–5 pages (start / middle / end) before moving on: the cut must fall on the binding and no text line may be clipped.

Needs `pdftoppm` (poppler, installed) and Pillow (available system-wide and in `../../esame/.venv`). ScanTailor Advanced between Stage 1 and 2 is optional but recommended for deskew/dewarp.

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
