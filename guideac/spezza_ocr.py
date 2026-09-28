#!/usr/bin/env python3
"""
Spezza l'output paginato di Marker (ocr/marker/singole/singole.md, prodotto con
--paginate_output) in un file per pagina: ocr/marker/pages/p-NNN.md, con la stessa
numerazione di pagine/p-NNN.png e ocr/tesseract/p-NNN.txt.

Uso: python3 spezza_ocr.py [ocr/marker/singole/singole.md]
"""
import os, re, sys

src = sys.argv[1] if len(sys.argv) > 1 else "ocr/marker/singole/singole.md"
dst = "ocr/marker/pages"
os.makedirs(dst, exist_ok=True)
text = open(src, encoding="utf-8").read()
# separatore Marker: riga "{N}-----...----" (N = indice pagina, 0-based)
parts = re.split(r"\n*\{(\d+)\}-{10,}\n*", text)
# parts = [prima_del_primo_sep, n0, testo0, n1, testo1, ...]
pages = {}
for i in range(1, len(parts) - 1, 2):
    pages[int(parts[i]) + 1] = parts[i + 1].strip()
if parts[0].strip():
    pages.setdefault(1, parts[0].strip())
for n, body in sorted(pages.items()):
    open(os.path.join(dst, f"p-{n:03d}.md"), "w", encoding="utf-8").write(body + "\n")
print(f"{len(pages)} pagine scritte in {dst}/ (da {min(pages)} a {max(pages)})")
