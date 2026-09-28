#!/usr/bin/env python3
"""Genera dati.enc per la webapp a partire da fonte/wow_che_tratto_2.md.

1. Legge il Markdown della guida (convenzioni in fonte/CONTESTO.md).
2. Estrae solo cio' che serve all'app: il cammino dell'anno in breve, il contesto
   di ogni fase e le attivita' (Catechesi, Carita', Liturgia, Estate, Verifica).
3. Converte i testi in HTML (convertitore minimo, adatto a questo Markdown).
4. Cifra il JSON con AES-256-GCM, chiave derivata dalla password con PBKDF2-SHA256.

La guida e' protetta da copyright: nel repository finisce solo dati.enc.
Il JSON in chiaro si scrive solo con --chiaro (per debug, git-ignorato).

Uso:
    WCT_PASSWORD='...' python3 tools/build.py        # oppure chiede la password
    python3 tools/build.py --chiaro fonte/dati.json   # salva anche il JSON in chiaro
"""
import argparse
import base64
import getpass
import html
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

RADICE = Path(__file__).resolve().parent.parent
SORGENTE = RADICE / "fonte" / "wow_che_tratto_2.md"
USCITA = RADICE / "dati.enc"
ITERAZIONI = 310_000

# Sezioni della Prima parte tenute nella scheda "Anno" (titolo H4 -> etichetta)
ANNO_TENUTE = {
    "Domanda di vita: realizzazione – progetto": "La domanda di vita",
    "Domanda di vita declinata per fasce d'età": "La domanda di vita per i 9/11",
    "Il brano biblico": "Il brano biblico",
    "La domanda di vita e il Vangelo… in dialogo": "Domanda di vita e Vangelo",
    "Gli atteggiamenti": "Gli atteggiamenti",
    "L'iniziativa annuale 2026-2027": "L'Accademia del fumetto",
    "Lo slogan": "Lo slogan",
}


# ---------------------------------------------------------------- utilità

def slug(testo):
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def ripulisci(testo):
    """Toglie le parentesi quadre delle lettere ricostruite al bordo della foto: [li]mitato."""
    return re.sub(r"\[([A-Za-zÀ-ÿ']{1,5})\](?![(:^])", r"\1", testo)


def inline(testo):
    t = html.escape(ripulisci(testo), quote=False)
    t = re.sub(r"\[\^([\w-]+)\]", r'<sup class="nota">\1</sup>', t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\\$", "<br>", t)
    return t


def testo_piano(md):
    t = re.sub(r"<!--.*?-->", " ", md)
    t = re.sub(r"[#>*_|\\`]|\[!note\]|\[ \]", " ", ripulisci(t))
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------- Markdown -> HTML

def md_html(righe, livello_base=5):
    """Converte un frammento di Markdown in HTML. I titoli vengono rimappati:
    #×livello_base -> <h3>, livelli successivi -> <h4>."""
    out, note = [], []
    i = 0
    n = len(righe)

    def lista(i, indent):
        ordinata = bool(re.match(r"\s*\d+\. ", righe[i]))
        tag = "ol" if ordinata else "ul"
        parti = [f"<{tag}>"]
        while i < n:
            r = righe[i]
            m = re.match(r"(\s*)(?:[-*]|\d+\.) (.*)", r)
            if not m:
                break
            rientro = len(m.group(1))
            if rientro < indent:
                break
            if rientro > indent:
                sotto, i = lista(i, rientro)
                parti[-1] = parti[-1].removesuffix("</li>") + sotto + "</li>"
                continue
            voce = m.group(2)
            if voce.startswith("[ ] ") or voce.startswith("[x] "):
                voce = f'<label class="check"><input type="checkbox"> {inline(voce[4:])}</label>'
            else:
                voce = inline(voce)
            parti.append(f"<li>{voce}</li>")
            i += 1
        parti.append(f"</{tag}>")
        return "".join(parti), i

    while i < n:
        r = righe[i]
        s = r.strip()
        if not s or re.fullmatch(r"<!--.*-->", s):
            i += 1
            continue
        m = re.match(r"(#+) (.*)", r)
        if m:
            h = 3 if len(m.group(1)) <= livello_base else 4
            out.append(f"<h{h}>{inline(m.group(2))}</h{h}>")
            i += 1
            continue
        m = re.match(r"\[\^([\w-]+)\]: (.*)", r)
        if m:
            note.append(f'<li><sup>{m.group(1)}</sup> {inline(m.group(2))}</li>')
            i += 1
            continue
        if re.match(r"\s*(?:[-*]|\d+\.) ", r):
            blocco, i = lista(i, len(r) - len(r.lstrip()))
            out.append(blocco)
            continue
        if s.startswith(">"):
            citazione = []
            while i < n and righe[i].strip().startswith(">"):
                citazione.append(re.sub(r"^\s*> ?", "", righe[i]))
                i += 1
            m = re.match(r"\[!note\]\s*(.*)", citazione[0])
            if m:
                titolo = f"<strong>{inline(m.group(1))}</strong>" if m.group(1) else ""
                out.append(f'<aside class="box">{titolo}{md_html(citazione[1:], livello_base)}</aside>')
            else:
                out.append(f"<blockquote>{md_html(citazione, livello_base)}</blockquote>")
            continue
        if s.startswith("|"):
            tab = []
            while i < n and righe[i].strip().startswith("|"):
                celle = [c.strip() for c in righe[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in celle):
                    tab.append(celle)
                i += 1
            testa = "".join(f"<th>{inline(c)}</th>" for c in tab[0])
            corpo = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in rr) + "</tr>" for rr in tab[1:])
            out.append(f'<div class="tab"><table><thead><tr>{testa}</tr></thead><tbody>{corpo}</tbody></table></div>')
            continue
        # paragrafo: righe consecutive non vuote e non di altro tipo
        par = []
        while i < n:
            r = righe[i]
            s = r.strip()
            if not s or re.match(r"#+ |\s*(?:[-*]|\d+\.) |>|\||\[\^[\w-]+\]: |<!--", s if not r.startswith(" ") else r):
                break
            par.append(inline(s))
            i += 1
        if not par:  # riga non riconosciuta: evita cicli infiniti
            par.append(inline(s))
            i += 1
        out.append(f"<p>{' '.join(par)}</p>")
    if note:
        out.append(f'<ol class="note-pie">{"".join(note)}</ol>')
    return "".join(out)


# ---------------------------------------------------------------- albero dei titoli

class Nodo:
    def __init__(self, livello, titolo, pagina):
        self.livello, self.titolo, self.pagina = livello, titolo, pagina
        self.righe, self.figli = [], []

    def tutte_le_righe(self):
        """Corpo del nodo compresi i sotto-titoli (Markdown originale)."""
        r = list(self.righe)
        for f in self.figli:
            r.append("#" * f.livello + " " + f.titolo)
            r.extend(f.tutte_le_righe())
        return r

    def pagine(self):
        p = [self.pagina]
        righe = [r for r in self.tutte_le_righe() if r.strip()]
        # un segnapagina in coda appartiene alla sezione successiva
        while righe and re.match(r"<!-- p\. \d+", righe[-1].strip()):
            righe.pop()
        for riga in righe:
            m = re.match(r"<!-- p\. (\d+)", riga.strip())
            if m:
                p.append(int(m.group(1)))
        return min(p), max(p)


def albero(testo):
    radice = Nodo(0, "", 1)
    pila = [radice]
    pagina = 1
    for riga in testo.splitlines():
        m = re.match(r"<!-- p\. (\d+)", riga.strip())
        if m:
            pagina = int(m.group(1))
        m = re.match(r"(#{1,6}) (.*)", riga)
        if m:
            liv = len(m.group(1))
            while pila[-1].livello >= liv:
                pila.pop()
            nodo = Nodo(liv, m.group(2).strip(), pagina)
            pila[-1].figli.append(nodo)
            pila.append(nodo)
        else:
            pila[-1].righe.append(riga)
    return radice


def trova(nodo, titolo):
    for f in nodo.figli:
        if f.titolo.startswith(titolo):
            return f
        t = trova(f, titolo)
        if t:
            return t
    return None


def scopo(nodo):
    """Riga in corsivo sotto l'icona della tappa (*I ragazzi …*)."""
    for r in nodo.righe:
        s = r.strip()
        if s.startswith("*") and not s.startswith("**") and s.endswith("*"):
            return s.strip("*").strip()
        if s and not s.startswith("<!--"):
            break
    return ""


def senza_scopo(righe):
    fatto = False
    out = []
    for r in righe:
        s = r.strip()
        if not fatto and s.startswith("*") and not s.startswith("**") and s.endswith("*"):
            fatto = True
            continue
        out.append(r)
    return out


# ---------------------------------------------------------------- estrazione

def ambito_di(titolo):
    if titolo.startswith("Liturgia"):
        return "Liturgia"
    if titolo.startswith("Carità"):
        return "Carità"
    if "catechesi" in titolo:
        return "Catechesi"
    if titolo.startswith("Verifica"):
        return "Verifica"
    if titolo.startswith("Tempo Estate"):
        return "Estate"
    return "Altro"


def dividi_titolo(t):
    parti = re.split(r" – ", t, maxsplit=1)
    return (parti[0], parti[1]) if len(parti) == 2 else (t, "")


def attivita(fase_n, blocco, tappa, titolo, righe, pagine, **extra):
    corpo = righe
    d = {
        "id": f"f{fase_n}-{slug(titolo)}"[:60],
        "fase": fase_n,
        "ambito": ambito_di(blocco.titolo),
        "blocco": blocco.titolo,
        "tappa": tappa,
        "titolo": titolo,
        "pagine": list(pagine),
        "html": md_html(corpo).removeprefix(f"<h3>{inline(titolo)}</h3>"),
        "testo": testo_piano("\n".join(corpo)),
    }
    d.update(extra)
    tag = []
    if re.search(r"Pista A\b", titolo):
        tag.append("Pista A")
    if re.search(r"Pista B\b", titolo):
        tag.append("Pista B")
    if "Piccolissimi" in d["testo"]:
        tag.append("Piccolissimi")
    d["tag"] = tag
    return d


def estrai_blocco(fase_n, blocco):
    amb = ambito_di(blocco.titolo)
    out = []
    if amb in ("Verifica",):
        out.append(attivita(fase_n, blocco, "Verifica", blocco.titolo, blocco.tutte_le_righe(),
                            blocco.pagine(), scopo="Checklist per rileggere la fase con gli altri educatori."))
        return out
    if amb == "Liturgia":
        for h4 in blocco.figli:
            tappa, titolo = dividi_titolo(h4.titolo)
            out.append(attivita(fase_n, blocco, tappa, titolo or tappa, h4.tutte_le_righe(), h4.pagine()))
        return out
    scopo_ereditato = ""
    for h4 in blocco.figli:
        sc = scopo(h4) or scopo_ereditato
        if h4.titolo == "Confronto":
            scopo_ereditato = sc
            continue
        if not h4.titolo.startswith("Confronto"):
            scopo_ereditato = ""
        if h4.titolo.startswith("Appunti per la festa") or h4.titolo == "Campo scuola":
            nome = h4.titolo.replace("Appunti per la f", "F")
            nome = nome[0].upper() + nome[1:]
            primo = h4.figli[0].titolo if h4.figli else nome
            out.append(attivita(fase_n, blocco, nome, primo if h4.figli else nome,
                                senza_scopo(h4.tutte_le_righe()), h4.pagine(), scopo=sc))
            continue
        precedente = None
        for h5 in h4.figli:
            if h5.titolo.startswith("Suggerimenti per l'educatore") and precedente:
                precedente["html"] += '<aside class="box sugg"><strong>Suggerimenti per l\'educatore</strong>' + md_html(h5.tutte_le_righe()) + "</aside>"
                precedente["testo"] += " " + testo_piano("\n".join(h5.tutte_le_righe()))
                precedente["pagine"][1] = max(precedente["pagine"][1], h5.pagine()[1])
                continue
            intro = [r for r in senza_scopo(h4.righe) if r.strip() and not r.strip().startswith("<!--")]
            righe = (intro if not precedente else []) + h5.tutte_le_righe()
            tappa = h4.titolo
            precedente = attivita(fase_n, blocco, tappa, h5.titolo, righe, list(h5.pagine()), scopo=sc)
            out.append(precedente)
    return out


def contesto_fase(fase):
    sezioni = []
    atteggiamento = ""
    obiettivi = []
    for h4 in fase.figli:
        if h4.livello != 4:
            continue
        corpo = h4.tutte_le_righe()
        if h4.titolo == "Obiettivi":
            for r in corpo:
                m = re.match(r"Atteggiamento prevalente: \*\*(.+?)\*\*", r.strip())
                if m:
                    atteggiamento = m.group(1).capitalize()
                m = re.match(r"- (.*)", r.strip())
                if m:
                    obiettivi.append(inline(m.group(1)).rstrip(";."))
            corpo = [r for r in corpo if not r.strip().startswith("Atteggiamento prevalente")]
        sezioni.append({"titolo": h4.titolo, "html": md_html(corpo, 5)})
    return atteggiamento, obiettivi, sezioni


def sommario_fase(fase):
    """Lista annidata della pagina di sommario (prima dell'Idea di fondo)."""
    righe = [r for r in fase.righe if re.match(r"\s*- ", r)]
    return md_html(righe) if righe else ""


def estrai(testo):
    rad = albero(testo)
    seconda = trova(rad, "Seconda parte")
    fasi, att = [], []
    for fase in seconda.figli:
        m = re.match(r"(\w+) fase – (.*)", fase.titolo)
        if not m:
            continue
        n = len(fasi) + 1
        atteggiamento, obiettivi, sezioni = contesto_fase(fase)
        blocchi = [b for b in fase.figli if b.livello == 3]
        fasi.append({
            "n": n,
            "titolo": m.group(2),
            "etichetta": f"{m.group(1)} fase",
            "pagine": list(fase.pagine()),
            "atteggiamento": atteggiamento,
            "obiettivi": obiettivi,
            "sezioni": sezioni,
            "blocchi": [b.titolo for b in blocchi],
        })
        for b in blocchi:
            att.extend(estrai_blocco(n, b))

    anno = []
    cammino = trova(rad, "Il cammino dell'anno")
    for titolo, etichetta in ANNO_TENUTE.items():
        nodo = trova(cammino, titolo)
        if nodo is None:
            sys.exit(f"Sezione dell'anno non trovata: {titolo}")
        righe = nodo.tutte_le_righe()
        if titolo.startswith("Domanda di vita declinata"):
            nodo = trova(nodo, "9/11")
            righe = nodo.tutte_le_righe()
        anno.append({"titolo": etichetta, "pagine": list(nodo.pagine()), "html": md_html(righe, 5)})

    # id univoci
    visti = {}
    for a in att:
        if a["id"] in visti:
            visti[a["id"]] += 1
            a["id"] += f"-{visti[a['id']]}"
        else:
            visti[a["id"]] = 1
    return {
        "titolo": "Wow, che tratto! 2",
        "sottotitolo": "Guida per l'educatore · Acr 9-11 · 2026-2027",
        "anno": anno,
        "fasi": fasi,
        "attivita": att,
    }


# ---------------------------------------------------------------- cifratura

def cifra(dati, password):
    salt, iv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERAZIONI)
    chiave = kdf.derive(password.encode("utf-8"))
    ct = AESGCM(chiave).encrypt(iv, json.dumps(dati, ensure_ascii=False).encode("utf-8"), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITERAZIONI, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chiaro", type=Path, help="salva anche il JSON in chiaro (solo per debug, non committare)")
    ap.add_argument("--solo-chiaro", action="store_true", help="non cifrare (richiede --chiaro)")
    args = ap.parse_args()

    dati = estrai(SORGENTE.read_text(encoding="utf-8"))
    per_ambito = {}
    for a in dati["attivita"]:
        per_ambito[a["ambito"]] = per_ambito.get(a["ambito"], 0) + 1
    print(f"{len(dati['fasi'])} fasi, {len(dati['attivita'])} schede: {per_ambito}")

    if args.chiaro:
        args.chiaro.write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"JSON in chiaro: {args.chiaro}")
    if args.solo_chiaro:
        return
    password = os.environ.get("WCT_PASSWORD") or getpass.getpass("Password: ")
    if len(password) < 8:
        sys.exit("Password troppo corta (minimo 8 caratteri).")
    USCITA.write_text(json.dumps(cifra(dati, password)), encoding="utf-8")
    print(f"Scritto {USCITA.relative_to(RADICE)} ({USCITA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
