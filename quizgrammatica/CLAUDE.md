# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

No build step or server required. Open any HTML file directly in a browser:

```
open quiz_app.html
```

`quiz_app.html` is the main consolidated app. The `Quiz_*.html` files are older standalone versions with hardcoded question sets.

## Project structure

This is a static Italian grammar exam study tool — no frameworks, no dependencies, vanilla JS + HTML/CSS only.

**Data layer:**
- `paniere.json` — canonical question bank (361 questions), source of truth
- `paniere.js` — identical data exposed as `window.PANIERE` for browser `<script src>` loading

**Main app (`quiz_app.html`):**
- Loads `paniere.js` via `<script src="paniere.js">` in the same directory
- Draws 30 random questions per session from the filtered pool
- Supports topic filtering via checkboxes at start screen

**Legacy standalone quizzes:**
- `Quiz_Grammatica.html`, `Quiz_Grammatica_2.html`, `Quiz_Grammatica_3.html` — grammar topic only
- `Quiz_Italiano_Contemporaneo.html` — contemporary Italian topic
- `Quiz_Storia_Lingua_Morgana.html` — language history topic

These embed their questions inline; they do not use `paniere.js`.

## Question schema

Every question in `paniere.json` / `paniere.js` follows:

```json
{
  "id": "gram-001",
  "topic": "grammatica",        // "grammatica" | "contemporaneo" | "lingua"
  "source": "Book title (Author)",
  "q": "Question text",
  "opts": ["A...", "B...", "C...", "D..."],
  "correct": 2,                 // 0-indexed into opts
  "explanation": "..."
}
```

Current topic counts: `grammatica` 186, `contemporaneo` 95, `lingua` 80.

## Keeping paniere.js in sync

`paniere.json` and `paniere.js` must always contain identical questions. `paniere.js` wraps the array as:

```js
window.PANIERE = [ /* same content as paniere.json */ ];
```

When adding or editing questions, update both files.