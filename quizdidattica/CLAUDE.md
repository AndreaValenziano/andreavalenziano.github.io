# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```
open index.html
```

No build step. Vanilla JS + HTML/CSS; open directly in a browser.

## Structure

- `index.html` — the quiz app (inline CSS + JS, loads `paniere.js` at runtime)
- `paniere.json` / `paniere.js` — question bank (300 questions); **both files must always be kept in sync**
- `*.pdf` — source study materials (3 texts)
- `*.md` — extracted/summarised notes from the PDFs
- `screen_esame/` — exam session screenshots (reference only)

`paniere.js` is just a wrapper: `window.PANIERE = [ /* same content as paniere.json */ ]`.

## Question schema

```json
{
  "id": "did-001",
  "fonte": "didattica",
  "source": "Didattica dell'italiano come lingua prima (Cignetti, Viale, Demartini, Fornara)",
  "capitolo": "Cap. 1 — Che cos'è la didattica dell'italiano",
  "q": "...",
  "opts": ["A", "B", "C", "D"],
  "correct": 1,
  "explanation": "..."
}
```

- `fonte` — `"didattica"` (210 questions), `"lettura"` (45), `"meme"` (45)
- `capitolo` — optional; present only on `didattica` questions
- ID prefixes: `did-`, `let-`, `meme-`
- `correct` — 0-based index into `opts`

**Key difference from quizgrammatica**: this schema uses `fonte` (not `topic`) and has no `topic` field.

## App behaviour

- Start screen lets the user filter by source (`fonte`); all three checked by default
- Draws 31 random questions from the filtered pool
- Options are shuffled on each render; `correct` tracks the original index, not the displayed position
- "Retry" replays the same 31 questions; "New quiz" returns to the start screen

## Adding questions

1. Add entries to `paniere.json`
2. Mirror the identical array in `paniere.js` (wrapped as `window.PANIERE = [...]`)
3. Keep IDs sequential within each prefix (`did-NNN`, `let-NNN`, `meme-NNN`)