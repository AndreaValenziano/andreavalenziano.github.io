#!/usr/bin/env python3
"""
risolvi2.py — Risolutore esami v2.

Differenze rispetto a esame/risolvi.py (v1):
- NIENTE OCR locale (Tesseract): le domande vengono estratte dagli screenshot
  con la visione di Claude + output strutturato JSON. Conteggio e opzioni esatti,
  niente segmentazione euristica che fonde più domande in un blocco.
- Deduplica automatica: gli screenshot a scorrimento si sovrappongono (la stessa
  domanda compare in fondo a uno screen e in cima al successivo).
- Risposte ancorate al materiale: ogni risposta deve includere una CITAZIONE
  testuale del materiale che la giustifica, più il flag nel_materiale verificabile.
- Il paniere.json (se presente nella cartella materia) entra nella knowledge base
  come fonte primaria (domande ufficiali con risposta corretta).
- Prompt caching sulla knowledge base: la prima risposta scalda la cache, le
  successive la riusano (~90% di risparmio sull'input).

Pipeline: knowledge base → estrazione visiva parallela → dedup → risposte → salvataggio.

Uso:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 risolvi2.py --immagini quizdidattica/screen_esame --materia quizdidattica
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("⚠ Manca il pacchetto 'anthropic'. Installa con: pip install -r requirements.txt")
    sys.exit(1)

# ─── Costanti ─────────────────────────────────────────────────────────────────

MODELLI = {
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5",
}
# Modelli che supportano l'adaptive thinking (usato per le risposte)
ADAPTIVE_OK = ("claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6",
               "claude-sonnet-4-6", "claude-fable-5")

RECAP_KEYWORDS = ("ripasso", "recap", "completo", "riepilogo", "comprensiv")

MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".gif": "image/gif", ".webp": "image/webp"}

PROMPT_ESTRAZIONE = """Sei un trascrittore di esami a scelta multipla in italiano.
Ricevi lo screenshot di una pagina d'esame online. Ogni domanda ha:
- (opzionale) una riga di intestazione con la fonte (titolo del libro / capitolo)
- il testo della domanda
- 4 opzioni di risposta, ognuna preceduta da un cerchietto radio-button

Trascrivi OGNI domanda COMPLETAMENTE visibile nello screenshot, dall'alto in basso.

Regole:
- Trascrivi testo e opzioni VERBATIM (correggi solo refusi tipografici evidenti).
- Le opzioni vanno NELL'ORDINE A SCHERMO, dall'alto in basso. Non riordinarle,
  non aggiungerne, non saltarne.
- Ignora i cerchietti dei radio-button: non fanno parte del testo dell'opzione.
- Se sopra la domanda c'è una riga con la fonte (libro/capitolo), mettila nel
  campo "fonte"; altrimenti lascia "fonte" vuoto.
- Una domanda è "completa" solo se il suo testo E tutte le sue opzioni sono
  interamente visibili. Se una domanda è tagliata dal bordo dello screenshot
  (sopra o sotto), includila comunque ma con "completa": false.
- Se lo screenshot non contiene domande, restituisci una lista vuota."""

SCHEMA_ESTRAZIONE = {
    "type": "object",
    "properties": {
        "domande": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fonte": {"type": "string",
                              "description": "Riga di intestazione con libro/capitolo, vuota se assente"},
                    "domanda": {"type": "string"},
                    "opzioni": {"type": "array", "items": {"type": "string"}},
                    "completa": {"type": "boolean",
                                 "description": "true se domanda e opzioni sono interamente visibili"},
                },
                "required": ["fonte", "domanda", "opzioni", "completa"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["domande"],
    "additionalProperties": False,
}

PROMPT_RISPOSTE = """Sei un assistente d'esame. Rispondi a domande a scelta multipla
basandoti ESCLUSIVAMENTE sul materiale di studio fornito qui sotto.

Regole:
- Cerca nel materiale il passaggio che risponde alla domanda. Se il materiale
  contiene una sezione PANIERE DI ESERCITAZIONE (presente solo nelle prove),
  cerca prima lì una domanda equivalente (anche riformulata) e usa la sua
  risposta corretta.
- "posizione" è la posizione A SCHERMO dell'opzione corretta (1 = prima dall'alto).
- "citazione" è il passaggio testuale del materiale che giustifica la risposta,
  copiato verbatim (max ~50 parole). Se non trovi nulla nel materiale, lasciala vuota.
- "nel_materiale" è true SOLO se la citazione proviene davvero dal materiale.
- Se il materiale non copre la domanda, rispondi comunque con le tue conoscenze
  ma imposta nel_materiale=false e confidenza al massimo "media".
- Confidenza "alta" solo se la risposta è confermata esplicitamente dal materiale."""

SCHEMA_RISPOSTE_BATCH = {
    "type": "object",
    "properties": {
        "risposte": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "numero": {"type": "integer", "description": "Numero della domanda (Dn)"},
                    "posizione": {"type": "integer", "enum": [1, 2, 3, 4]},
                    "spiegazione": {"type": "string", "description": "Motivazione breve (1-2 frasi)"},
                    "citazione": {"type": "string",
                                  "description": "Passaggio verbatim del materiale che giustifica la risposta, vuoto se assente"},
                    "nel_materiale": {"type": "boolean"},
                    "confidenza": {"type": "string", "enum": ["alta", "media", "bassa"]},
                },
                "required": ["numero", "posizione", "spiegazione", "citazione",
                             "nel_materiale", "confidenza"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["risposte"],
    "additionalProperties": False,
}


def _con_retry_429(fn, descrizione: str, max_tentativi: int = 6):
    """Esegue fn(); sui 429 aspetta quanto indicato da retry-after e riprova."""
    ultimo: Exception | None = None
    for tentativo in range(1, max_tentativi + 1):
        try:
            return fn()
        except anthropic.RateLimitError as e:
            ultimo = e
            try:
                attesa = int(e.response.headers.get("retry-after", "30"))
            except (TypeError, ValueError):
                attesa = 30
            attesa += 2
            print(f"    ⏳ rate limit ({descrizione}): aspetto {attesa}s e riprovo "
                  f"({tentativo}/{max_tentativi})", flush=True)
            time.sleep(attesa)
    raise ultimo  # type: ignore[misc]


# ─── Stage 1: Knowledge base ──────────────────────────────────────────────────

def estrai_flashcard_ecologia(html_path: Path) -> str:
    """Estrae le coppie {q, a} dal blocco <script> di quizecologia/index.html."""
    testo = html_path.read_text(encoding="utf-8")
    pattern = r'\{\s*q:\s*["\']([^"\']+)["\']\s*,\s*a:\s*["\']([^"\']+)["\']\s*\}'
    coppie = re.findall(pattern, testo)
    if not coppie:
        return ""
    righe = [f"D: {q}\nR: {a}" for q, a in coppie]
    return "## Flashcard ecologia\n\n" + "\n\n".join(righe)


def estrai_paniere(materia_path: Path) -> str:
    """
    Converte paniere.json in testo per la knowledge base.
    ATTENZIONE: i panieri di questo repo sono generati da Claude, non sono
    domande ufficiali — all'esame reale non ci saranno. Vanno inclusi (--paniere)
    solo nelle prove, dove il quiz di esercitazione attinge proprio dal paniere.
    """
    p = materia_path / "paniere.json"
    if not p.exists():
        return ""
    try:
        dati = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("    ⚠ paniere.json illeggibile, saltato", flush=True)
        return ""
    blocchi = []
    for q in dati:
        opts = q.get("opts") or []
        corr = q.get("correct")
        if not q.get("q") or corr is None or not (0 <= corr < len(opts)):
            continue
        righe = [f"D: {q['q']}", f"R corretta: {opts[corr]}"]
        if q.get("explanation"):
            righe.append(f"Spiegazione: {q['explanation']}")
        blocchi.append("\n".join(righe))
    if not blocchi:
        return ""
    return ("## PANIERE DI ESERCITAZIONE — domande generate con risposta corretta (solo prove)\n\n"
            + "\n\n".join(blocchi))


def estrai_pdf(pdf_path: Path) -> str:
    """
    Estrae il testo da un PDF con pdftotext (poppler).
    Il risultato viene salvato in <nome>.extracted.md accanto al PDF (cache).
    """
    cache_path = pdf_path.parent / (pdf_path.stem + ".extracted.md")
    if cache_path.exists():
        print(f"    [cache] {cache_path.name}", flush=True)
        return cache_path.read_text(encoding="utf-8")

    print(f"    [estrazione PDF] {pdf_path.name} …", flush=True)
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
        )
        testo = result.stdout.strip()
    except FileNotFoundError:
        print("    ⚠ pdftotext non trovato — installa poppler (brew install poppler)", flush=True)
        return ""
    except subprocess.TimeoutExpired:
        print(f"    ⚠ timeout nell'estrazione di {pdf_path.name}", flush=True)
        return ""

    if not testo:
        print(f"    ⚠ nessun testo estratto da {pdf_path.name} (PDF scansionato?)", flush=True)
        return ""

    contenuto = f"## {pdf_path.stem}\n\n{testo}"
    cache_path.write_text(contenuto, encoding="utf-8")
    print(f"    ✓ estratto {pdf_path.name}: {len(testo.split()):,} parole → cache {cache_path.name}", flush=True)
    return contenuto


def _fingerprint_blocco(testo: str) -> str:
    """Fingerprint leggero per rilevare materiali duplicati (stesso contenuto, nomi diversi)."""
    normalizzato = testo.lower()
    normalizzato = re.sub(r"lOMoARcPSD\|[\w]+", "", normalizzato)  # watermark Studocu
    normalizzato = re.sub(r"\s+", " ", normalizzato).strip()
    return hashlib.sha256(normalizzato[:3000].encode("utf-8")).hexdigest()


def costruisci_knowledge_base(materia_path: Path, con_paniere: bool = False,
                              con_pdf: bool = False) -> str:
    """
    Knowledge base dalla cartella materia.
    Priorità: paniere.json (solo prove) > flashcard HTML > recap .md > altri .md > PDF.
    I PDF sono in genere gli stessi contenuti dei riassunti .md: di default vengono
    saltati se esiste almeno un .md, per stare dentro i rate limit di input.
    """
    blocchi: list[str] = []
    fingerprints_visti: set[str] = set()

    def _aggiungi_se_nuovo(etichetta: str, testo: str, blocco: str) -> None:
        fp = _fingerprint_blocco(testo)
        if fp in fingerprints_visti:
            print(f"    ⊘ {etichetta} saltato (duplicato)", flush=True)
            return
        fingerprints_visti.add(fp)
        blocchi.append(blocco)
        print(f"    ✓ {etichetta}: {len(testo.split()):,} parole", flush=True)

    if con_paniere:
        paniere = estrai_paniere(materia_path)
        if paniere:
            _aggiungi_se_nuovo("paniere.json", paniere, paniere)

    html_index = materia_path / "index.html"
    if html_index.exists():
        fc = estrai_flashcard_ecologia(html_index)
        if fc:
            _aggiungi_se_nuovo("flashcard index.html", fc, fc)

    md_files = sorted(
        p for p in materia_path.glob("*.md")
        if not p.name.endswith(".extracted.md")
        and not p.name.startswith(("esame_", "esame2_", "domande_estratte", "risultati_"))
    )
    md_stems = {p.stem for p in md_files}

    recap_files = [p for p in md_files if any(k in p.stem.lower() for k in RECAP_KEYWORDS)]
    altri_md = [p for p in md_files if p not in recap_files]

    for md_path in recap_files + altri_md:
        testo = md_path.read_text(encoding="utf-8")
        _aggiungi_se_nuovo(md_path.name, testo, f"## FILE: {md_path.name}\n\n{testo}")

    pdf_candidati = [p for p in sorted(materia_path.glob("*.pdf")) if p.stem not in md_stems]
    if con_pdf or not md_files:
        for pdf_path in pdf_candidati:
            estratto = estrai_pdf(pdf_path)
            if estratto:
                testo_grezzo = estratto.split("\n\n", 2)[-1] if "\n\n" in estratto else estratto
                _aggiungi_se_nuovo(pdf_path.name, testo_grezzo, estratto)
    elif pdf_candidati:
        print(f"    ⊘ {len(pdf_candidati)} PDF saltati: ci sono già riassunti .md "
              "(usa --includi-pdf per forzarli)", flush=True)

    if not blocchi:
        print("  ⚠ Nessun materiale trovato nella cartella della materia!", flush=True)
        sys.exit(1)

    kb = "\n\n---\n\n".join(blocchi)
    parole_tot = len(kb.split())
    print(f"\n    Knowledge base totale: {parole_tot:,} parole", flush=True)
    return kb


# ─── Stage 2: estrazione visiva ───────────────────────────────────────────────

def _testo_da_risposta(resp) -> str:
    if resp.stop_reason == "refusal":
        raise RuntimeError("richiesta rifiutata dai classificatori di sicurezza")
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("output troncato (max_tokens) — riprova")
    return next(b.text for b in resp.content if b.type == "text")


def estrai_da_immagine(client: anthropic.Anthropic, model: str, img_path: Path) -> list[dict]:
    """Estrae le domande da uno screenshot con la visione di Claude."""
    media = MEDIA_TYPES.get(img_path.suffix.lower())
    if media is None:
        raise RuntimeError(f"formato immagine non supportato: {img_path.suffix}")
    data = base64.standard_b64encode(img_path.read_bytes()).decode("utf-8")

    resp = client.messages.create(
        model=model,
        max_tokens=8000,
        system=PROMPT_ESTRAZIONE,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": media, "data": data}},
                {"type": "text",
                 "text": "Trascrivi tutte le domande visibili in questo screenshot."},
            ],
        }],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA_ESTRAZIONE}},
    )
    return json.loads(_testo_da_risposta(resp))["domande"]


def _chiave_domanda(testo: str) -> str:
    """Chiave normalizzata per deduplicare la stessa domanda tra screenshot sovrapposti."""
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
    return t[:160]


def estrazione_parallela(client, model: str, immagini: list[Path], workers: int) -> tuple[list[dict], list[str]]:
    """
    Estrae le domande da tutte le immagini in parallelo, mantenendo l'ordine
    degli screenshot, deduplicando le sovrapposizioni e scartando le domande
    tagliate (incomplete) che ricompaiono complete in un altro screenshot.
    Ritorna (domande, avvisi).
    """
    risultati: dict[int, list[dict]] = {}
    avvisi: list[str] = []

    def _job(idx: int, img: Path):
        return idx, _con_retry_429(lambda: estrai_da_immagine(client, model, img), img.name)

    # La prima immagine da sola: se fallisce per autenticazione/configurazione
    # ci si ferma subito invece di ripetere lo stesso errore per ogni immagine.
    try:
        _, prime = _job(0, immagini[0])
        risultati[0] = prime
        print(f"    ✓ {immagini[0].name}: {len(prime)} domande", flush=True)
    except (anthropic.AnthropicError, TypeError) as e:  # TypeError: SDK senza credenziali
        sys.exit(f"⚠ Errore API alla prima richiesta: {e}\n"
                 "  Controlla che ANTHROPIC_API_KEY sia impostata.")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_job, i, immagini[i]) for i in range(1, len(immagini))]
        for fut in as_completed(futures):
            try:
                idx, domande = fut.result()
                risultati[idx] = domande
                print(f"    ✓ {immagini[idx].name}: {len(domande)} domande", flush=True)
            except Exception as e:  # noqa: BLE001 — un'immagine fallita non blocca le altre
                idx = futures.index(fut) + 1  # +1: la prima immagine è processata a parte
                risultati[idx] = []
                avvisi.append(f"immagine {immagini[idx].name} fallita: {e}")
                print(f"    ⚠ {immagini[idx].name}: {e}", flush=True)

    # Dedup nell'ordine degli screenshot. Le versioni complete vincono su quelle tagliate.
    per_chiave: dict[str, dict] = {}
    ordine: list[str] = []
    for i in range(len(immagini)):
        for d in risultati.get(i, []):
            d["immagine"] = immagini[i].name
            chiave = _chiave_domanda(d["domanda"])
            if not chiave:
                continue
            gia = per_chiave.get(chiave)
            if gia is None:
                per_chiave[chiave] = d
                ordine.append(chiave)
            elif not gia["completa"] and d["completa"]:
                per_chiave[chiave] = d  # sostituisce la versione tagliata

    domande = [per_chiave[k] for k in ordine]
    incomplete = [d for d in domande if not d["completa"]]
    for d in incomplete:
        avvisi.append(f"domanda tagliata in {d['immagine']} e mai vista completa: «{d['domanda'][:70]}…»")
    n_opzioni_anomale = [d for d in domande if len(d["opzioni"]) != 4]
    for d in n_opzioni_anomale:
        avvisi.append(f"{len(d['opzioni'])} opzioni (attese 4): «{d['domanda'][:70]}…»")
    return domande, avvisi


# ─── Stage 3: risposte ────────────────────────────────────────────────────────

def _accorcia(testo: str, n: int) -> str:
    testo = " ".join(testo.split())
    return testo if len(testo) <= n else testo[: n - 1].rstrip() + "…"


def _formatta_domanda(d: dict) -> str:
    righe = []
    if d.get("fonte"):
        righe.append(f"Fonte indicata a schermo: {d['fonte']}")
    righe.append(f"Domanda: {d['domanda']}")
    for i, opt in enumerate(d["opzioni"], 1):
        righe.append(f"{i}. {opt}")
    return "\n".join(righe)


def _errore_risposta(msg: str) -> dict:
    return {"posizione": 0, "spiegazione": f"ERRORE: {msg}", "citazione": "",
            "nel_materiale": False, "confidenza": "bassa"}


def rispondi_chunk(client, model: str, system_blocks: list,
                   chunk: list[dict], offset: int) -> tuple[dict[int, dict], int]:
    """Risponde a un blocco di domande in UNA richiesta (il materiale si paga una
    volta per blocco, non per domanda). Ritorna ({numero: risposta}, cache_read)."""
    corpo = [f"### Domanda {offset + i}\n{_formatta_domanda(d)}"
             for i, d in enumerate(chunk, 1)]
    testo = (f"Rispondi a TUTTE le {len(chunk)} domande seguenti "
             f"(numerate da {offset + 1} a {offset + len(chunk)}), una risposta per "
             "ciascuna; nel campo 'numero' riporta il numero della domanda.\n\n"
             + "\n\n".join(corpo))
    kwargs = {"thinking": {"type": "adaptive"}} if model in ADAPTIVE_OK else {}
    # Il rate limiter non riserva il max_tokens richiesto (conta solo l'output
    # effettivo), quindi un tetto generoso non costa nulla: serve spazio per il
    # thinking + ~200 token a risposta, e un tetto basso tronca l'output
    # costringendo a dividere il blocco (= KB ripagata e attese in più).
    resp = client.messages.create(
        model=model,
        max_tokens=min(16000, 2000 + 450 * len(chunk)),
        system=system_blocks,
        messages=[{"role": "user", "content": testo}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA_RISPOSTE_BATCH}},
        **kwargs,
    )
    dati = json.loads(_testo_da_risposta(resp))["risposte"]
    cache_read = getattr(resp.usage, "cache_read_input_tokens", 0) or 0
    return {r["numero"]: r for r in dati}, cache_read


def _rispondi_blocco_adattivo(client, model: str, system_blocks: list,
                              chunk: list[dict], offset: int, stats: dict) -> dict[int, dict]:
    """Risponde a un blocco; se l'output viene troncato lo dimezza e riprova."""
    try:
        mappa, cache_read = _con_retry_429(
            lambda: rispondi_chunk(client, model, system_blocks, chunk, offset),
            f"D{offset + 1}–D{offset + len(chunk)}")
    except RuntimeError as e:
        if "troncato" in str(e) and len(chunk) > 1:
            meta = len(chunk) // 2
            print("    ✂ output troncato: divido il blocco in due", flush=True)
            m1 = _rispondi_blocco_adattivo(client, model, system_blocks, chunk[:meta], offset, stats)
            m2 = _rispondi_blocco_adattivo(client, model, system_blocks, chunk[meta:], offset + meta, stats)
            return {**m1, **m2}
        raise
    stats["richieste"] += 1
    if cache_read:
        stats["cache_hit"] += 1
        stats["token_cache"] += cache_read
    return mappa


def risposte_a_blocchi(client, model: str, kb: str, domande: list[dict],
                       batch: int) -> tuple[list[dict], dict]:
    """Risponde a tutte le domande in blocchi sequenziali da `batch`.

    Il rate limiter stima TUTTA la KB a ogni richiesta, anche quando poi viene
    letta dalla cache (visto sugli header: input-tokens-remaining va a 0 dopo
    ogni blocco). Quindi meno blocchi = meno attese: il default è il blocco
    unico. La cache resta utile (sul costo, non sulle attese) quando i blocchi
    sono più di uno — e nel blocco unico viene saltata: la scrittura costa +25%."""
    blocco_kb: dict = {"type": "text", "text": "=== MATERIALE DI STUDIO ===\n\n" + kb}
    if len(domande) > batch:
        blocco_kb["cache_control"] = {"type": "ephemeral"}
    system_blocks = [{"type": "text", "text": PROMPT_RISPOSTE}, blocco_kb]
    stats = {"richieste": 0, "cache_hit": 0, "token_cache": 0}
    mappa_tot: dict[int, dict] = {}

    for start in range(0, len(domande), batch):
        chunk = domande[start:start + batch]
        try:
            mappa = _rispondi_blocco_adattivo(client, model, system_blocks, chunk, start, stats)
        except Exception as e:  # noqa: BLE001 — un blocco fallito non blocca i successivi
            print(f"    ⚠ blocco D{start + 1}–D{start + len(chunk)} fallito: {e}", flush=True)
            mappa = {start + i: _errore_risposta(str(e)) for i in range(1, len(chunk) + 1)}
        mappa_tot.update(mappa)
        for n in range(start + 1, start + len(chunk) + 1):
            r = mappa_tot.get(n)
            d = domande[n - 1]
            dom = _accorcia(d["domanda"], 45)
            if r and 1 <= (r.get("posizione") or 0) <= len(d["opzioni"]):
                opz = _accorcia(d["opzioni"][r["posizione"] - 1], 40)
                print(f"    ✓ D{n} «{dom}» → {r['posizione']}. «{opz}» ({r['confidenza']})", flush=True)
            else:
                print(f"    ⚠ D{n} «{dom}» → ?", flush=True)

    risposte = [mappa_tot.get(n) or _errore_risposta("risposta mancante nel blocco")
                for n in range(1, len(domande) + 1)]
    return risposte, stats


# ─── Stage 4: salvataggio ─────────────────────────────────────────────────────

def salva_domande(materia_path: Path, immagini: list[Path], domande: list[dict],
                  avvisi: list[str], attese: int, ts: str) -> tuple[Path, Path]:
    md_path = materia_path / f"esame2_domande_{ts}.md"
    json_path = materia_path / f"esame2_domande_{ts}.json"

    righe = [
        f"# Domande estratte — {ts}",
        "",
        f"- **Immagini**: `{immagini[0].parent}` ({len(immagini)} file)",
        f"- **Domande**: {len(domande)} (attese: {attese})",
    ]
    if avvisi:
        righe.append("")
        righe.append("## ⚠ Avvisi")
        righe.extend(f"- {a}" for a in avvisi)
    righe.append("")
    for n, d in enumerate(domande, 1):
        righe.append(f"## D{n}. {d['domanda']}")
        righe.extend(f"{i}. {opt}" for i, opt in enumerate(d["opzioni"], 1))
        righe.append("")

    md_path.write_text("\n".join(righe), encoding="utf-8")
    json_path.write_text(json.dumps(domande, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, json_path


def salva_risposte(materia_path: Path, domande: list[dict], risposte: list[dict],
                   model: str, ts: str) -> Path:
    path = materia_path / f"esame2_risposte_{ts}.md"
    righe = [f"# Esame — Foglio risposte (v2)", "",
             f"- **Generato**: {ts} · modello `{model}`",
             f"- **Domande**: {len(domande)}", ""]

    da_verificare = [
        (n, d, r) for n, (d, r) in enumerate(zip(domande, risposte), 1)
        if r["confidenza"] != "alta" or not r["nel_materiale"] or not r["posizione"]
    ]
    if da_verificare:
        righe.append("## ⚠ Domande da verificare")
        for n, d, r in da_verificare:
            motivo = "errore" if not r["posizione"] else (
                f"{r['confidenza']}" + ("" if r["nel_materiale"] else ", non nel materiale"))
            righe.append(f"- D{n} ({motivo}) · {d['domanda'][:80]}")
        righe.append("")
    righe.append("---")
    righe.append("")

    for n, (d, r) in enumerate(zip(domande, risposte), 1):
        righe.append(f"## D{n}. {d['domanda']}")
        for i, opt in enumerate(d["opzioni"], 1):
            marca = " ✅" if i == r["posizione"] else ""
            righe.append(f"{i}.{marca} {opt}")
        nel_mat = "✓" if r["nel_materiale"] else "✗"
        righe.append("")
        righe.append(f"> ✅ **Risposta: {r['posizione'] or '?'}** · confidenza: {r['confidenza']} · nel materiale: {nel_mat}")
        if r["spiegazione"]:
            righe.append(f"> {r['spiegazione']}")
        if r["citazione"]:
            righe.append(f"> 📖 «{r['citazione']}»")
        righe.append("")
        righe.append("---")
        righe.append("")

    path.write_text("\n".join(righe), encoding="utf-8")
    return path


# ─── Main ─────────────────────────────────────────────────────────────────────

def _elenca_immagini(cartella: Path) -> list[Path]:
    """Immagini ordinate per data di modifica (l'ordine in cui sono state scattate).
    L'ordine per nome è inaffidabile: '3.51 PM' verrebbe dopo '10.51 AM'."""
    imgs = [p for p in cartella.iterdir()
            if p.suffix.lower() in MEDIA_TYPES and not p.name.startswith(".")]
    return sorted(imgs, key=lambda p: (p.stat().st_mtime, p.name))


def main() -> None:
    parser = argparse.ArgumentParser(description="Risolutore esami v2 — estrazione visiva con Claude")
    parser.add_argument("--immagini", required=True, help="Cartella degli screenshot delle domande")
    parser.add_argument("--materia", required=True, help="Cartella del materiale di studio")
    parser.add_argument("--modello", default="sonnet",
                        help="Modello per le risposte: sonnet (default) / haiku / opus, o un ID completo")
    parser.add_argument("--modello-visione", default="haiku",
                        help="Modello per l'estrazione dagli screenshot (default haiku: "
                             "la trascrizione è semplice, conta la velocità)")
    parser.add_argument("--workers", type=int, default=8,
                        help="Richieste parallele per l'estrazione (default 8)")
    parser.add_argument("--batch", type=int, default=30,
                        help="Domande per richiesta nelle risposte (default 30 = blocco unico: "
                             "il rate limiter conta tutta la KB a ogni richiesta, quindi meno "
                             "richieste = meno attese; diviso in automatico se l'output trabocca)")
    parser.add_argument("--attese", type=int, default=30, help="Numero di domande attese (default 30)")
    parser.add_argument("--solo-domande", action="store_true",
                        help="Estrai solo le domande, senza rispondere (per il flusso manuale in chat)")
    parser.add_argument("--paniere", action="store_true",
                        help="Includi paniere.json nella knowledge base. SOLO per le prove: "
                             "il paniere è generato da Claude, all'esame reale non ci sarà")
    parser.add_argument("--includi-pdf", action="store_true",
                        help="Includi anche i PDF pur in presenza di riassunti .md "
                             "(KB più grande: attenzione ai rate limit)")
    args = parser.parse_args()

    immagini_path = Path(args.immagini)
    materia_path = Path(args.materia)
    if not immagini_path.is_dir():
        sys.exit(f"⚠ Cartella immagini non trovata: {immagini_path}")
    if not materia_path.is_dir():
        sys.exit(f"⚠ Cartella materia non trovata: {materia_path}")

    model = MODELLI.get(args.modello, args.modello)
    model_visione = MODELLI.get(args.modello_visione, args.modello_visione)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        client = anthropic.Anthropic()
    except anthropic.AnthropicError as e:
        sys.exit(f"⚠ Client Anthropic non inizializzato: {e}\n"
                 "  Imposta la variabile d'ambiente ANTHROPIC_API_KEY.")

    immagini = _elenca_immagini(immagini_path)
    if not immagini:
        sys.exit(f"⚠ Nessuna immagine in {immagini_path}")

    print(f"\n📚 Knowledge base da {materia_path} …", flush=True)
    kb = "" if args.solo_domande else costruisci_knowledge_base(
        materia_path, con_paniere=args.paniere, con_pdf=args.includi_pdf)

    t0 = time.monotonic()
    print(f"\n👁  Estrazione visiva da {len(immagini)} screenshot (modello {model_visione}) …", flush=True)
    domande, avvisi = estrazione_parallela(client, model_visione, immagini, args.workers)
    print(f"    ⏱ estrazione: {time.monotonic() - t0:.0f}s", flush=True)

    print(f"\n    Domande uniche estratte: {len(domande)} (attese: {args.attese})", flush=True)
    if len(domande) != args.attese:
        avvisi.insert(0, f"estratte {len(domande)} domande ma ne erano attese {args.attese} "
                         "— controlla che gli screenshot coprano tutto l'esame")
        print(f"    ⚠ {avvisi[0]}", flush=True)

    if not domande:
        sys.exit("⚠ Nessuna domanda estratta — controlla gli screenshot.")

    md_dom, json_dom = salva_domande(materia_path, immagini, domande, avvisi, args.attese, ts)
    print(f"\n✅ Domande:  {md_dom}", flush=True)
    print(f"✅ JSON:     {json_dom}", flush=True)

    if args.solo_domande:
        print("\nFlusso manuale: allega il file domande + il materiale in una chat Claude "
              "e incolla il prompt da esame2/PROMPT_CHAT.md", flush=True)
        return

    t1 = time.monotonic()
    print(f"\n🤖 Risposte ({len(domande)} domande, blocchi da {args.batch}, modello {model}) …", flush=True)
    risposte, stats = risposte_a_blocchi(client, model, kb, domande, args.batch)
    print(f"    ⏱ risposte: {time.monotonic() - t1:.0f}s", flush=True)

    if stats["richieste"] > 1:
        print(f"    💾 cache: letta in {stats['cache_hit']}/{stats['richieste']} richieste "
              f"({stats['token_cache']:,} token a ~1/10 del prezzo)", flush=True)
        if stats["cache_hit"] == 0:
            print("    ⚠ cache mai letta — segnalamelo se ricapita", flush=True)

    md_risp = salva_risposte(materia_path, domande, risposte, model, ts)
    basse = sum(1 for r in risposte if r["confidenza"] != "alta" or not r["nel_materiale"])
    print(f"\n✅ Risposte: {md_risp}", flush=True)
    print(f"   {len(domande)} domande · {basse} da verificare (vedi ⚠ in testa al file)", flush=True)


if __name__ == "__main__":
    main()
