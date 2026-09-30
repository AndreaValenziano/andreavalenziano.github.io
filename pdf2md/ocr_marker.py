#!/usr/bin/env python3
"""
Stadio 2 (Marker) a blocchi, con timeout e nuovi tentativi.

Marker delega l'OCR a un llama-server (Surya) che ogni tanto si blocca a meta' di una
richiesta (0% CPU, nessun progresso): lanciato sull'intero volume in un colpo solo si
perde tutto. Qui il PDF viene elaborato a blocchi di N pagine; un blocco che supera il
timeout viene ucciso (insieme al llama-server) e rilanciato. I blocchi gia' completati
vengono saltati, quindi lo script si puo' rilanciare dopo un'interruzione.

Uso (dalla cartella del libro):
  DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib \
  python3 ../ocr_marker.py singole.pdf [--blocco 20] [--timeout-min 20]
Output: ocr/marker/blocchi/*/  ->  ocr/marker/singole/singole.md (concatenato, separatori
{N}---- con N 0-based), poi usare ../spezza_ocr.py per ottenere ocr/marker/pages/p-NNN.md.
"""
import argparse, os, signal, subprocess, sys, time

MARKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "marker_single")


def pagine_pdf(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    return int(next(l.split()[-1] for l in out.splitlines() if l.startswith("Pages:")))


def uccidi_llama():
    subprocess.run(["pkill", "-f", "llama-server.*surya"], capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default="ocr/marker")
    ap.add_argument("--blocco", type=int, default=20)
    ap.add_argument("--timeout-min", type=float, default=20)
    ap.add_argument("--tentativi", type=int, default=3)
    args = ap.parse_args()

    env = dict(os.environ, DYLD_LIBRARY_PATH=os.environ.get("DYLD_LIBRARY_PATH",
                                                             "/opt/homebrew/opt/expat/lib"))
    n = pagine_pdf(args.pdf)
    stem = os.path.splitext(os.path.basename(args.pdf))[0]
    parti = []
    for a in range(0, n, args.blocco):
        b = min(a + args.blocco, n) - 1
        d = os.path.join(args.out, "blocchi", f"{a:04d}-{b:04d}")
        md = os.path.join(d, stem, stem + ".md")
        parti.append(md)
        if os.path.exists(md):
            print(f"[{a}-{b}] gia' fatto", flush=True)
            continue
        for t in range(1, args.tentativi + 1):
            t0 = time.time()
            print(f"[{a}-{b}] tentativo {t}...", flush=True)
            log = open(os.path.join(args.out, f"blocco_{a:04d}.log"), "w")
            p = subprocess.Popen([MARKER, args.pdf, "--page_range", f"{a}-{b}", "--output_dir", d,
                                  "--output_format", "markdown", "--disable_image_extraction",
                                  "--paginate_output", "--disable_tqdm"],
                                 stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            try:
                p.wait(timeout=args.timeout_min * 60)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                print(f"[{a}-{b}] bloccato dopo {args.timeout_min} min, lo uccido", flush=True)
            uccidi_llama()
            if os.path.exists(md):
                print(f"[{a}-{b}] ok in {time.time() - t0:.0f} s", flush=True)
                break
        else:
            sys.exit(f"[{a}-{b}] fallito dopo {args.tentativi} tentativi: vedi i log in {args.out}")

    dest = os.path.join(args.out, "singole")
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "singole.md"), "w", encoding="utf-8") as f:
        for md in parti:
            f.write(open(md, encoding="utf-8").read().rstrip() + "\n\n")
    print(f"{n} pagine -> {dest}/singole.md")


if __name__ == "__main__":
    main()
