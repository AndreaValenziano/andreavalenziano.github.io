#!/usr/bin/env python3
"""
PDF da condividere: una pagina del libro per pagina PDF, nell'ordine delle pagine
STAMPATE, senza duplicati, con livello di testo OCR (ricercabile e selezionabile).
Le pagine assenti dalle scansioni diventano un segnaposto "pagina N non disponibile".

Input: la cartella pagine/ (p-NNN.png) e pagine_stampate.tsv (file <TAB> pagina <TAB> nota;
pagina '-' = escludere). Richiede tesseract (ita) e pdfunite (poppler).

Uso: python3 pdf_condivisione.py 9-11 "9-11/Wow che tratto 2 - guida educatore.pdf"
     opzioni: --lato 1800 (lato lungo in px)  --qualita 75  --senza-ocr
"""
import argparse, os, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont


def leggi_mappa(path):
    pagine = {}
    for riga in open(path, encoding="utf-8"):
        if riga.startswith("#") or not riga.strip():
            continue
        f, n = riga.rstrip("\n").split("\t")[:2]
        if n.strip() != "-":
            pagine[int(n)] = f.strip()
    return pagine


def segnaposto(n, size):
    im = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size[0] // 22)
    except OSError:
        font = ImageFont.load_default()
    d.text((size[0] // 2, size[1] // 2), f"Pagina {n}\nnon presente nelle scansioni",
           fill=(120, 120, 120), font=font, anchor="mm", align="center")
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cartella", help="cartella del libro (contiene pagine/ e pagine_stampate.tsv)")
    ap.add_argument("output")
    ap.add_argument("--lato", type=int, default=1800)
    ap.add_argument("--qualita", type=int, default=75)
    ap.add_argument("--senza-ocr", action="store_true")
    args = ap.parse_args()

    pagine = leggi_mappa(os.path.join(args.cartella, "pagine_stampate.tsv"))
    first, last = min(pagine), max(pagine)
    ref = Image.open(os.path.join(args.cartella, "pagine", pagine[first] + ".png"))
    ref.thumbnail((args.lato, args.lato))

    with tempfile.TemporaryDirectory() as wd:
        def prepara(n):
            if n in pagine:
                im = Image.open(os.path.join(args.cartella, "pagine", pagine[n] + ".png")).convert("RGB")
                im.thumbnail((args.lato, args.lato))
            else:
                im = segnaposto(n, ref.size)
            jpg = os.path.join(wd, f"{n:04d}.jpg")
            # 150 dpi nominali: la pagina reale del libro e' ~21 cm, quindi l'ingombro a
            # schermo/stampa resta plausibile
            im.save(jpg, quality=args.qualita, dpi=(150, 150))
            out = os.path.join(wd, f"{n:04d}")
            if args.senza_ocr or n not in pagine:
                im.save(out + ".pdf", resolution=150)
            else:
                # tesseract incorpora il JPEG cosi' com'e' e sovrappone il testo invisibile
                subprocess.run(["tesseract", jpg, out, "-l", "ita", "--psm", "3", "pdf"],
                               check=True, capture_output=True)
            return out + ".pdf"

        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            pdfs = list(ex.map(prepara, range(first, last + 1)))
        subprocess.run(["pdfunite", *pdfs, args.output], check=True)

    mancanti = [n for n in range(first, last + 1) if n not in pagine]
    mb = os.path.getsize(args.output) / 1e6
    print(f"{args.output}: pp. {first}-{last} ({len(pdfs)} pagine, {mb:.0f} MB); segnaposto per {mancanti}")


if __name__ == "__main__":
    main()
