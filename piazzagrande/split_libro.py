#!/usr/bin/env python3
"""
Normalizza uno scanso fotografico di libro:
  - ruota (opzionale) le pagine di 90 gradi
  - divide ogni doppia pagina in due pagine singole
  - salta le pagine che sono gia' singole (copertina ecc.), anche in automatico
    riconoscendole dall'orientamento verticale
  - ricomprime a una dimensione ragionevole; opzionalmente salva anche i PNG

Uso:  python3 split_libro.py "PIAZZA GRANDE.pdf" singole.pdf --skip auto --rot 0 --dpi 144 --png pagine/
"""
import argparse, os, subprocess, tempfile
from PIL import Image, JpegImagePlugin  # noqa: F401 (registra il salvataggio JPEG usato dal PDF)

def render(pdf, dpi, workdir):
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf,
                    os.path.join(workdir, "pg")], check=True)
    return sorted(f for f in os.listdir(workdir) if f.startswith("pg-"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--skip", default="",
                    help="pagine gia' singole (es. 1,2) oppure 'auto' = pagine verticali")
    ap.add_argument("--dpi", type=int, default=144)
    ap.add_argument("--rot", type=int, default=0, help="90=antiorario, -90=orario, 0=nessuna")
    ap.add_argument("--offset", type=float, default=0.0,
                    help="sposta la linea di taglio in %% della larghezza (-20..20)")
    ap.add_argument("--png", default="",
                    help="cartella dove salvare anche le pagine singole come PNG (p-001.png ...)")
    ap.add_argument("--reuse", action="store_true",
                    help="non rendere/tagliare: ricompone il PDF dai PNG gia' presenti in --png")
    args = ap.parse_args()

    if args.reuse:
        files = sorted(f for f in os.listdir(args.png) if f.endswith(".png"))
        out = [Image.open(os.path.join(args.png, f)).convert("RGB") for f in files]
        out[0].save(args.output, save_all=True, append_images=out[1:],
                    resolution=args.dpi, quality=85)
        print(f"{len(out)} PNG -> {args.output}")
        return

    auto = args.skip.strip().lower() == "auto"
    skip = set() if auto else {int(x) for x in args.skip.split(",") if x.strip()}
    if args.png:
        os.makedirs(args.png, exist_ok=True)

    with tempfile.TemporaryDirectory() as wd:
        files = render(args.input, args.dpi, wd)
        out, log = [], []
        for i, f in enumerate(files, start=1):
            im = Image.open(os.path.join(wd, f)).convert("RGB")
            if args.rot:
                im = im.rotate(args.rot, expand=True)
            w, h = im.size
            single = (i in skip) or (auto and h > w)
            if single:                          # gia' singola e gia' dritta
                out.append(im); log.append(f"{i}->{len(out)}")
                continue
            cut = int(w / 2 + w * args.offset / 100)
            out.append(im.crop((0, 0, cut, h)))       # pagina sinistra
            out.append(im.crop((cut, 0, w, h)))       # pagina destra
            log.append(f"{i}->{len(out)-1},{len(out)}")
        if args.png:
            for n, im in enumerate(out, start=1):
                im.save(os.path.join(args.png, f"p-{n:03d}.png"))
        out[0].save(args.output, save_all=True, append_images=out[1:],
                    resolution=args.dpi, quality=85)
        print(f"{len(files)} pagine PDF -> {len(out)} pagine libro  ({args.output})")
        print("mappa pdf->libro:", " ".join(log))

if __name__ == "__main__":
    main()
