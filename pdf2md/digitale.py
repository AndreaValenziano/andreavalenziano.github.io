#!/usr/bin/env python3
"""
Strada "digitale": PDF con testo (esportati da Word, LaTeX, ...) -> Markdown, senza LLM.

pymupdf4llm ricava titoli (dimensione del font), grassetti/corsivi, elenchi e tabelle, toglie
intestazioni e piè di pagina e salva le immagini su file. Poi una pulizia deterministica:
- separatori di pagina -> commenti <!-- p. N --> (N = pagina del PDF, 1-based);
- immagini minuscole (icone, linee) scartate, immagini identiche deduplicate (stesso hash);
- righe vuote multiple compattate.
- immagini ridimensionate e convertite in JPEG (--max-lato).
Scrive anche immagini.tsv (file, pagina, larghezza, altezza, duplicato_di) per lo stadio delle
descrizioni (vedi descrizioni.py).

Uso (dalla cartella del documento):
  ../pdf2md/.venv/bin/python ../pdf2md/digitale.py "Sbobine 2.pdf" sbobine_2.raw.md [--img img] [--min-px 60]
"""
import argparse, hashlib, os, re, sys

import pymupdf4llm
from PIL import Image

IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def comprimi(path, max_lato):
    """PNG -> JPEG (fondo bianco sotto la trasparenza), lato lungo <= max_lato. Ritorna il nuovo percorso."""
    m = re.search(r"-(\d{4})-(\d+)\.\w+$", path)  # pymupdf4llm: <pdf>-<pagina 1-based>-<k>.png
    nome = f"p{int(m.group(1)):03d}-{m.group(2)}.jpg" if m else os.path.splitext(os.path.basename(path))[0] + ".jpg"
    nuovo = os.path.join(os.path.dirname(path), nome)
    with Image.open(path) as im:
        im = im.convert("RGBA")
        fondo = Image.new("RGB", im.size, "white")
        fondo.paste(im, mask=im.split()[3])
        fondo.thumbnail((max_lato, max_lato))
        fondo.save(nuovo, "JPEG", quality=85, optimize=True)
    os.remove(path)
    return nuovo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--img", default="img", help="cartella delle immagini estratte")
    ap.add_argument("--min-px", type=int, default=60, help="scarta immagini con lato minore sotto questa soglia")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--max-lato", type=int, default=1000,
                    help="ridimensiona le immagini (lato lungo) e le salva in JPEG: meno MB su git, meno token per le descrizioni")
    a = ap.parse_args()

    os.makedirs(a.img, exist_ok=True)
    md = pymupdf4llm.to_markdown(
        a.pdf, write_images=True, image_path=a.img, image_format="png", dpi=a.dpi,
        use_ocr=False, header=False, footer=False, page_separators=True, show_progress=False,
    )

    # Separatori di pagina "--- end of page.page_number=N ---" (N 1-based) -> commento all'inizio della pagina.
    parti = re.split(r"\n*-{3,} end of page\.page_number=(\d+) -{3,}\n*", md)
    corpo = []
    for i in range(0, len(parti), 2):
        testo = parti[i].strip()
        n = int(parti[i + 1]) if i + 1 < len(parti) else None
        if n is not None:
            corpo.append(f"<!-- p. {n} -->\n\n{testo}" if testo else f"<!-- p. {n} -->")
        elif testo:
            corpo.append(testo)
    md = "\n\n".join(corpo)

    # Immagini: scarta le minuscole, deduplica per hash.
    visti, righe_tsv = {}, []
    def sostituisci(m):
        path = m.group(1)
        if not os.path.exists(path):
            return m.group(0)
        with Image.open(path) as im:
            w, h = im.size
        if min(w, h) < a.min_px:
            os.remove(path)
            return ""
        digest = hashlib.sha1(open(path, "rb").read()).hexdigest()
        pagina = re.search(r"-(\d{4})-\d+\.", path)
        pagina = int(pagina.group(1)) if pagina else ""
        if digest in visti:
            os.remove(path)
            righe_tsv.append(f"{path}\t{pagina}\t{w}\t{h}\t{visti[digest]}")
            return f"![]({visti[digest]})"
        path = comprimi(path, a.max_lato)
        visti[digest] = path
        righe_tsv.append(f"{path}\t{pagina}\t{w}\t{h}\t")
        return f"![]({path})"
    md = IMG_RE.sub(sostituisci, md)

    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(md)
    with open("immagini.tsv", "w", encoding="utf-8") as f:
        f.write("file\tpagina\tlarghezza\taltezza\tduplicato_di\n" + "\n".join(righe_tsv) + "\n")

    uniche = sum(1 for r in righe_tsv if r.endswith("\t"))
    print(f"{a.out}: {len(md.split())} parole; immagini uniche {uniche}, duplicate {len(righe_tsv) - uniche}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
