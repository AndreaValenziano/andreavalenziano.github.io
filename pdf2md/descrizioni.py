#!/usr/bin/env python3
"""
Prepara i lotti di immagini da far descrivere ad agenti in parallelo (uno per lotto).

Per ogni immagine unica di immagini.tsv scrive nel lotto il percorso, la pagina e il contesto
(il testo subito prima e subito dopo nel Markdown grezzo), così l'agente non deve leggere il
documento intero: legge solo le sue immagini (già ridotte da digitale.py) e questo file.

Uso (dalla cartella del documento):
  python3 ../pdf2md/descrizioni.py sbobine_2.raw.md [--lotti 6] [--contesto 300]
Output: descrizioni/lotto_K.md (ingresso per l'agente K); l'agente scrive descrizioni/lotto_K.tsv
nel formato di ../pdf2md/ISTRUZIONI_IMMAGINI.md, poi rifinisci.py le inserisce nel Markdown.
"""
import argparse, csv, os, re

PIC_TEXT = re.compile(r"<!-- Start of picture text -->.*?<!-- End of picture text -->", re.S)


def pulisci(t):
    t = PIC_TEXT.sub(" ", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]+\)|<!--.*?-->|[*_#]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--lotti", type=int, default=6)
    ap.add_argument("--contesto", type=int, default=300, help="caratteri di testo prima/dopo l'immagine")
    a = ap.parse_args()

    md = open(a.md, encoding="utf-8").read()
    righe = list(csv.DictReader(open("immagini.tsv", encoding="utf-8"), delimiter="\t"))
    uniche = [r for r in righe if not r["duplicato_di"]]

    voci = []
    for r in uniche:
        i = md.find(f"]({r['file']})")
        i = md.rfind("![", 0, i)
        prima = pulisci(md[max(0, i - 3 * a.contesto):i])[-a.contesto:]
        j = md.find(")", i) + 1
        dopo = pulisci(md[j:j + 3 * a.contesto])[:a.contesto]
        voci.append(f"## {r['file']} (p. {r['pagina']})\n\nPrima: …{prima}\n\nDopo: {dopo}…\n")

    os.makedirs("descrizioni", exist_ok=True)
    per_lotto = -(-len(voci) // a.lotti)
    for k in range(a.lotti):
        parte = voci[k * per_lotto:(k + 1) * per_lotto]
        if parte:
            with open(f"descrizioni/lotto_{k + 1}.md", "w", encoding="utf-8") as f:
                f.write("\n".join(parte))
            print(f"descrizioni/lotto_{k + 1}.md: {len(parte)} immagini")


if __name__ == "__main__":
    main()
