# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a static GitHub Pages site hosting Italian-language exam study tools. The quiz apps (quizgrammatica, quizecologia, quizdidattica) are vanilla JS + HTML/CSS with no build step. The `esame/` tool is a separate Python CLI with its own virtualenv and dependencies — see below.

## Sub-projects

### quizgrammatica/

Italian grammar exam quiz. See `quizgrammatica/CLAUDE.md` for full details.

- `quiz_app.html` — main app (draws 30 random questions per session, supports topic filtering)
- `paniere.json` / `paniere.js` — shared question bank (361 questions); **both files must always be kept in sync**
- `Quiz_*.html` — legacy standalone quizzes with inline questions (do not use `paniere.js`)

### quizecologia/

Ecology & sustainability flashcard quiz.

- `index.html` — single self-contained file; questions are hardcoded as `{ q, a }` objects inside the `<script>` block
- All questions are term-definition pairs (no multiple choice, no `correct` index)

### quizdidattica/

Study materials for the didattica exam. Contains PDF files, `paniere.json` (question bank, same schema as quizgrammatica), and `screen_esame/` — ~32 PNG screenshots of real exam questions.

`quizdidattica/` doubles as the `--materia` folder for `esame/risolvi.py`; `screen_esame/` is used as the `--immagini` input:

```
./esame/avvia.sh --immagini quizdidattica/screen_esame --materia quizdidattica --modello sonnet
```

No HTML quiz app yet.

### esame/

Python CLI tool that solves multiple-choice exam questions: local OCR (Tesseract, Italian) + LLM answers grounded strictly in the supplied study material. 4-stage pipeline: knowledge base → parallel OCR → answers → save results.

**Key files:**
- `risolvi.py` — main script; `python3` entrypoint `main()`, argparse CLI
- `avvia.sh` — bash wrapper; sets `DYLD_LIBRARY_PATH` (macOS libexpat workaround) and runs `risolvi.py` via `.venv/`
- `requirements.txt` — `anthropic`, `pytesseract`, `Pillow`, `ollama`, `numpy`

**System binaries required (not in requirements.txt):** Tesseract OCR, poppler (`pdftotext`), Ollama server.

**CLI arguments:**
- `--immagini PATH` *(required)* — folder of question screenshots
- `--materia PATH` *(required)* — folder of study materials (`.md`, `.pdf`, `index.html`)
- `--backend` — `claude` (default) or `ollama`
- `--modello` — `haiku`/`sonnet` for Claude; Ollama model name otherwise
- `--embed-modello` — Ollama embedding model (default `nomic-embed-text`)
- `--top-k` — retrieved passages per question for RAG (default 6)
- `--workers` — parallel threads (default 8; capped to 2 for Ollama)

**Two backends:**
- `claude` (default) — Anthropic API, forced tool-use for structured JSON, prompt caching. Models: `haiku` → `claude-haiku-4-5`, `sonnet` → `claude-sonnet-4-6`. Requires `ANTHROPIC_API_KEY` env var.
- `ollama` — local/offline RAG: chunk KB → embed (`nomic-embed-text`, cached to `.cache/emb_*.npz`) → cosine retrieval → `ollama.chat` (default model `qwen2.5:7b`).

**Material loading priority:** inline flashcards in `index.html` (special-cased for `quizecologia`) › recap `.md` files (stem contains *ripasso*, *recap*, *completo*, *riepilogo*, or *comprensiv*) › other `.md` files › PDFs via `pdftotext`. Does **not** read `paniere.json`.

**Output:** `esame/risultati_YYYYMMDD_HHMMSS.md` — OCR text + answers per question.

## Patterns

**quizgrammatica question schema** (used in `paniere.json` / `paniere.js`):
```json
{ "id": "gram-001", "topic": "grammatica", "source": "...", "q": "...", "opts": ["A", "B", "C", "D"], "correct": 2, "explanation": "..." }
```
Topics: `"grammatica"` (186), `"contemporaneo"` (95), `"lingua"` (80).

**quizecologia question schema** (inline in `index.html`):
```js
{ q: "Term", a: "Definition" }
```

When adding questions to `quizgrammatica`, update both `paniere.json` and `paniere.js`. `paniere.js` wraps the array as `window.PANIERE = [...]`.