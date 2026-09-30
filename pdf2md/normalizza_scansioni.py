#!/usr/bin/env python3
"""
Stadio 1 generalizzato: normalizza scansioni di un libro provenienti da PIU' PDF di
tipo diverso e produce una pagina del libro per file (p-001.png, p-002.png, ...),
nell'ordine dei PDF e delle pagine.

Ogni PDF ha una modalita':
  piana    scansione da scanner piano: una pagina del libro appoggiata in un angolo
           del foglio A4. Ritaglia automaticamente il bordo inferiore (sfondo grigio o
           coperchio) e i margini laterali cercando il salto di luminosita' piu' netto.
  singola  foto gia' ritagliata di una pagina singola: nessun taglio.
  doppia   foto di una doppia pagina: taglio sulla rilegatura, cercata come la colonna
           piu' scura nella fascia centrale (40-60% della larghezza). Le pagine che dopo
           la rotazione risultano verticali sono trattate come singole.

La rotazione /Rotate dei metadati PDF e' gia' applicata da pdftoppm; --rot serve solo
se le foto sono storte davvero.

Uso:
  python3 normalizza_scansioni.py OUT_DIR  1.pdf:piana 2.pdf:piana 3.pdf:singola 4.pdf:doppia
  opzioni: --dpi-piana 200  --taglio-fisso 0.5 (disattiva la ricerca della rilegatura)
Scrive anche OUT_DIR/../mappa_pagine.txt (pdf:pagina -> p-NNN, con la colonna di taglio).
"""
import argparse, os, subprocess, tempfile
import numpy as np
from PIL import Image


def render(pdf, dpi, wd):
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf, os.path.join(wd, "pg")], check=True)
    return [os.path.join(wd, f) for f in sorted(os.listdir(wd)) if f.startswith("pg-")]


def smooth(v, k):
    return np.convolve(v, np.ones(k) / k, mode="same")


def edge(profile, lo, hi, k):
    """indice del salto di luminosita' piu' netto in profile[lo:hi]"""
    d = np.abs(np.diff(smooth(profile, k)))
    return lo + int(np.argmax(d[lo:hi]))


def ritaglia_piana(im, lim):
    g = np.asarray(im.convert("L"), dtype=float)
    h, w = g.shape
    k = max(3, h // 200)
    # il libro e' appoggiato nell'angolo in alto a sinistra: le finestre di ricerca
    # sono strette apposta, altrimenti il "salto" trovato e' un titolo o una foto
    bottom = edge(g.mean(1), int(h * lim["basso"][0]), int(h * lim["basso"][1]), k)
    cols = g[: int(bottom * .9)].mean(0)
    right = edge(cols, int(w * lim["destra"][0]), int(w * lim["destra"][1]), k)
    left = edge(cols, int(w * .005), int(w * lim["sinistra"]), k)
    return im.crop((left, 0, right, bottom)), f"crop x{left}-{right} y0-{bottom}"


def rilegatura(im, fisso):
    w, h = im.size
    if fisso is not None:
        return int(w * fisso)
    # la rilegatura e' una "valle" di luminosita' continua su quasi tutte le righe;
    # la colonna piu' scura in media si fa ingannare da foto e calendari, la valle no
    small = im.convert("L").resize((w // 4, h // 4))
    g = np.asarray(small, dtype=float)
    sh, sw = g.shape
    band = g[int(sh * .1): int(sh * .9)]
    band = np.apply_along_axis(lambda r: smooth(r, 3), 1, band)
    d = max(4, sw // 60)
    lo, hi = int(sw * .42), int(sw * .58)
    score = [np.mean(band[:, c] < np.minimum(band[:, c - d], band[:, c + d]) - 2)
             for c in range(lo, hi)]
    return int((lo + int(np.argmax(score))) * w / sw)


def miniatura(im, T=320):
    t = im.copy()
    t.thumbnail((T, T))
    return t


def anteprima(thumbs, out, T=320):
    """foglio di controllo: doppie pagine con la linea di taglio, piane col riquadro"""
    from PIL import ImageDraw
    cols = 6
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (T + 8), rows * (T + 20)), (80, 80, 80))
    d = ImageDraw.Draw(sheet)
    for k, (tag, t, marks, w0) in enumerate(thumbs):
        s = t.size[0] / w0
        td = ImageDraw.Draw(t)
        for kind, v in marks:
            if kind == "cut":
                td.line([(v * s, 0), (v * s, t.size[1])], fill="red", width=2)
            else:  # "crop xL-R y0-B"
                x, y = v.split()[1:]
                l, r = map(int, x[1:].split("-")); b = int(y.split("-")[1])
                td.rectangle([l * s, 0, r * s, b * s], outline="red", width=2)
        x0, y0 = (k % cols) * (T + 8), (k // cols) * (T + 20)
        sheet.paste(t, (x0, y0 + 18))
        d.text((x0 + 3, y0 + 3), tag, fill="yellow")
    sheet.save(out, quality=80)
    print("anteprima:", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("pdfs", nargs="+", help="file.pdf:modalita' (piana|singola|doppia)")
    ap.add_argument("--dpi-piana", type=int, default=200)
    ap.add_argument("--dpi-foto", type=int, default=72,
                    help="72 = risoluzione nativa delle foto iPhone esportate da Quartz")
    ap.add_argument("--rot", type=int, default=0)
    ap.add_argument("--taglio-fisso", type=float, default=None)
    ap.add_argument("--tagli", default="",
                    help="correzioni manuali della rilegatura, es. '4.pdf:5=0.49,6.pdf:4=0.51'")
    ap.add_argument("--piana-basso", default="0.645-0.70",
                    help="finestra (frazione dell'altezza) dove cercare il piede della pagina")
    ap.add_argument("--piana-destra", default="0.85-0.995")
    ap.add_argument("--piana-sinistra", type=float, default=0.06)
    ap.add_argument("--anteprima", default="",
                    help="salva un foglio JPEG con i tagli disegnati, per il controllo visivo")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    rng = lambda t: tuple(float(x) for x in t.split("-"))
    lim = {"basso": rng(args.piana_basso), "destra": rng(args.piana_destra),
           "sinistra": args.piana_sinistra}
    manual = {}
    for t in filter(None, args.tagli.split(",")):
        k, v = t.split("=")
        manual[k.strip()] = float(v)
    thumbs = []
    n, log = 0, ["# pdf:pagina -> file in pagine/ (sx, dx) [dettagli taglio]"]
    for spec in args.pdfs:
        pdf, mode = spec.rsplit(":", 1)
        with tempfile.TemporaryDirectory() as wd:
            dpi = args.dpi_piana if mode == "piana" else args.dpi_foto
            for i, f in enumerate(render(pdf, dpi, wd), start=1):
                im = Image.open(f).convert("RGB")
                if args.rot:
                    im = im.rotate(args.rot, expand=True)
                w, h = im.size
                tag = f"{os.path.basename(pdf)}:{i:<3}"
                if mode == "piana":
                    crop, info = ritaglia_piana(im, lim)
                    thumbs.append((tag, miniatura(im), [("box", info)], w))
                    outs = [crop]
                elif mode == "doppia" and w > h:
                    key = f"{os.path.basename(pdf)}:{i}"
                    fr = manual.get(key, args.taglio_fisso)
                    cut = int(w * fr) if fr is not None else rilegatura(im, None)
                    outs = [im.crop((0, 0, cut, h)), im.crop((cut, 0, w, h))]
                    info = f"taglio x={cut} ({cut / w:.1%})" + (" manuale" if key in manual else "")
                    thumbs.append((tag, miniatura(im), [("cut", cut)], w))
                else:
                    outs, info = [im], "singola"
                names = []
                for o in outs:
                    n += 1
                    o.save(os.path.join(args.out_dir, f"p-{n:03d}.png"), compress_level=1)
                    names.append(f"p-{n:03d}")
                log.append(f"{tag} -> {' '.join(names):<15} [{info}]")
                print(log[-1], flush=True)
    if args.anteprima:
        anteprima(thumbs, args.anteprima)
    mappa = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)), "mappa_pagine.txt")
    open(mappa, "w").write("\n".join(log) + "\n")
    print(f"{n} pagine in {args.out_dir}; mappa in {mappa}")


if __name__ == "__main__":
    main()
