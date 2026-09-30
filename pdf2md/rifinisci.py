#!/usr/bin/env python3
"""
Ultimo stadio della strada "digitale": Markdown grezzo (digitale.py) -> Markdown finale.

Tutto deterministico, le decisioni stanno in file del documento (rilanciabile a piacere):
- --rimuovi TESTO (ripetibile): residui di intestazioni/piè di pagina che pymupdf4llm non ha tolto;
- titoli: toglie il markup (**, _, <u>), rimappa i livelli con --livelli "5:4,4:4" e applica
  titoli.tsv (<testo del titolo senza markup> TAB <livello>; 0 = non è un titolo, diventa testo);
- immagini: da descrizioni/*.tsv (vedi ISTRUZIONI_IMMAGINI.md) mette il titolo come alt text e la
  descrizione in un blockquote sotto l'immagine; il "picture text" grezzo accanto a un'immagine
  descritta viene tolto (la descrizione lo contiene già). Le immagini ripetute vengono descritte
  solo la prima volta.
- --titolo/--descrizione: intestazione del file finale.

Uso (dalla cartella del documento):
  python3 ../pdf2md/rifinisci.py sbobine_2.raw.md sbobine_2.md --rimuovi "Elena Di Leo" --livelli 5:4 \\
      --titolo "..." --descrizione "..."
Mai modificare a mano il file finale: correggere titoli.tsv / descrizioni/*.tsv e rilanciare.
"""
import argparse, glob, os, re, sys

PIC_TEXT = r"\s*<!-- Start of picture text -->.*?<!-- End of picture text -->"
MARKUP = re.compile(r"\*\*|__|</?u>|(?<!\w)_|_(?!\w)")


def testo_titolo(t):
    return re.sub(r" ([:.,;])", r"\1", re.sub(r"\s+", " ", MARKUP.sub("", t))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("out")
    ap.add_argument("--rimuovi", action="append", default=[])
    ap.add_argument("--livelli", default="", help='rimappa i livelli dei titoli, es. "5:4,6:4"')
    ap.add_argument("--titolo", default="")
    ap.add_argument("--descrizione", default="")
    a = ap.parse_args()
    md = open(a.raw, encoding="utf-8").read()

    for t in a.rimuovi:
        md = re.sub(r"[ \t]*" + re.escape(t) + r"[ \t]*", " ", md)
    md = re.sub(r"^[ \t]*(?:[-*]|<br>)?[ \t]*$", "", md, flags=re.M)

    livelli = dict(tuple(map(int, c.split(":"))) for c in a.livelli.split(",") if c)
    override = {}
    if os.path.exists("titoli.tsv"):
        for riga in open("titoli.tsv", encoding="utf-8"):
            if riga.strip() and not riga.startswith("#"):
                t, l = riga.rstrip("\n").rsplit("\t", 1)
                override[t.strip()] = int(l)
    usati = set()
    def titolo(m):
        grezzo = m.group(2)
        t = testo_titolo(grezzo)
        l = livelli.get(len(m.group(1)), len(m.group(1)))
        if t in override:
            usati.add(t)
            l = override[t]
            if l == 0:
                return grezzo.strip()
        return "#" * l + " " + t
    md = re.sub(r"^(#{1,6}) +(.+)$", titolo, md, flags=re.M)
    for t in set(override) - usati:
        print(f"attenzione: titolo non trovato in titoli.tsv: {t!r}", file=sys.stderr)

    desc = {}
    for f in sorted(glob.glob("descrizioni/lotto_*.tsv")):
        for riga in open(f, encoding="utf-8"):
            campi = riga.rstrip("\n").split("\t")
            if len(campi) >= 3:
                desc[campi[0].strip()] = (campi[1].strip(), campi[2].strip(), "\t".join(campi[3:]).strip())
    descritte = set()
    def immagine(m):
        f = m.group(1)
        if f not in desc:
            return m.group(0)
        tipo, alt, d = desc[f]
        s = f"![{alt}]({f})"
        if tipo == "contenuto" and d and f not in descritte:
            s += f"\n\n> **Immagine:** {d}"
        descritte.add(f)
        return s
    md = re.sub(r"!\[[^\]]*\]\(([^)]+)\)(?:" + PIC_TEXT + ")?", immagine, md, flags=re.S)
    # "picture text" rimasto (non accanto a un'immagine descritta): via se corto, altrimenti testo semplice.
    def pic(m):
        t = re.sub(r"\s*<br>\s*", " · ", m.group(1)).strip(" ·")
        return "" if len(t) < 80 else f"\n\n{t}\n\n"
    md = re.sub(r"<!-- Start of picture text -->(.*?)<!-- End of picture text -->", pic, md, flags=re.S)
    mancanti = set(re.findall(r"!\[\]\(([^)]+)\)", md))
    if mancanti:
        print(f"attenzione: {len(mancanti)} immagini senza descrizione, es. {sorted(mancanti)[:3]}", file=sys.stderr)

    md = re.sub(r"(\*\*|\w_|</u>) ([,.;:!?])", r"\1\2", md)  # "**parola** ," -> "**parola**,"
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    testa = ""
    if a.titolo:
        testa = f"# {a.titolo}\n\n"
        if a.descrizione:
            testa += f"> {a.descrizione}\n\n"
        md = re.sub(r"\A(<!-- p\. 1 -->\s*)# [^\n]*\n+", r"\1", md)
    open(a.out, "w", encoding="utf-8").write(testa + md)
    print(f"{a.out}: {len((testa + md).split())} parole, {len(re.findall(r'^#', md, re.M))} titoli, "
          f"{len(descritte)} immagini descritte", file=sys.stderr)


if __name__ == "__main__":
    main()
