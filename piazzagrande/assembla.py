#!/usr/bin/env python3
"""
Assembla md/blocco_*.md nel file finale piazza_grande_2026-2027.md seguendo l'ordine
delle pagine STAMPATE (i blocchi seguono l'ordine delle foto, che non coincide con
quello del libro). Le note a piè di pagina [^n] vengono rinumerate per pagina
([^p35-1]) per evitare collisioni tra capitoli.
"""
import glob, re, sys

PAGE_RE = re.compile(r"^<!-- p\. ([0-9]+)(\?)?[^\n]*?-->", re.M)

chunks = []  # (numero pagina, ordine di foto, testo)
order = 0
for f in sorted(glob.glob("md/blocco_*.md")):
    text = open(f, encoding="utf-8").read()
    pos = [(m.start(), int(m.group(1))) for m in PAGE_RE.finditer(text)]
    if not pos:
        sys.exit(f"{f}: nessun marcatore di pagina")
    if pos[0][0] > 0 and text[:pos[0][0]].strip():
        chunks.append((0, order, text[:pos[0][0]].strip())); order += 1
    for i, (start, n) in enumerate(pos):
        end = pos[i + 1][0] if i + 1 < len(pos) else len(text)
        body = text[start:end].strip()
        # note a piè di pagina: [^k] -> [^p{n}-k]
        body = re.sub(r"\[\^(\d+)\]", lambda m: f"[^p{n}-{m.group(1)}]", body)
        chunks.append((n, order, body)); order += 1

chunks.sort(key=lambda c: (c[0], c[1]))
out = ["# piazza grande 2026|2027 — Guida educatori giovani",
       "",
       "<!-- Trascrizione in Markdown della guida (Azione Cattolica Italiana – Settore giovani, Ave 2026). "
       "Ordine = pagine stampate del libro. Ogni pagina inizia con <!-- p. N -->. -->",
       ""]
prev = None
for n, _, body in chunks:
    if prev is not None and n > prev + 1:
        lab = f"p. {prev + 1}" if n - 1 == prev + 1 else f"pp. {prev + 1}-{n - 1}"
        out.append(f"<!-- {lab}: non fotografata / assente dal PDF -->\n")
    out.append(body + "\n")
    prev = max(prev or 0, n)
open("piazza_grande_2026-2027.md", "w", encoding="utf-8").write("\n".join(out))
pages = sorted({c[0] for c in chunks if c[0]})
print(f"{len(chunks)} blocchi di pagina, pagine {pages[0]}-{pages[-1]}, mancanti:",
      [p for p in range(pages[0], pages[-1] + 1) if p not in pages])
