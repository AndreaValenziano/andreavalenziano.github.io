#!/usr/bin/env python3
"""
risolvi.py — Risolutore domande d'esame: OCR locale + LLM con grounding

Backend Claude (default — identico a prima, richiede ANTHROPIC_API_KEY):
    python3 esame/risolvi.py --immagini ./img --materia quizgrammatica
    python3 esame/risolvi.py --immagini ./img --materia quizdidattica --modello sonnet

Backend Ollama (locale, gratuito, nessun rate limit):
    python3 esame/risolvi.py --immagini ./img --materia quizgrammatica --backend ollama
    python3 esame/risolvi.py --immagini ./img --materia quizdidattica --backend ollama
    python3 esame/risolvi.py --immagini ./img --materia quizdidattica --backend ollama \\
        --modello qwen2.5:7b --embed-modello nomic-embed-text --top-k 8

Pre-requisiti Ollama:
    ollama pull qwen2.5:7b          # modello chat (già presente)
    ollama pull nomic-embed-text    # modello embedding (~270 MB)

Output in tempo reale (appena ogni risposta arriva):
    [07] uso congiuntivo → "dubbio/opinione" (B)  ✓0.93
    [03] fonema consonantico → "occlusiva bilabiale" (A)  ⚠ non nel materiale ✗0.41
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image
import pytesseract

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore

try:
    import ollama
except ImportError:
    ollama = None  # type: ignore


# ─── Costanti ─────────────────────────────────────────────────────────────────

MODELLI_CLAUDE = {
    "haiku": "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-6",
}

OLLAMA_MODELLO_DEFAULT = "qwen2.5:7b"
OLLAMA_EMBED_DEFAULT   = "nomic-embed-text"

IMG_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}

# Keyword per riconoscere i file .md di recap/ripasso comprensivi (case-insensitive).
# I file il cui stem contiene almeno una di queste parole vengono caricati per primi
# nella knowledge base, prima degli altri .md.
RECAP_KEYWORDS = ("ripasso", "recap", "completo", "riepilogo", "comprensiv")

# System prompt per il backend Claude (con tool use strutturato)
SYSTEM_ISTRUZIONI = """\
Sei un assistente per esami universitari italiani.

REGOLA FONDAMENTALE: Rispondi ESCLUSIVAMENTE in base al MATERIALE DIDATTICO \
fornito nel secondo blocco di questo messaggio di sistema. NON usare la tua \
conoscenza generale o enciclopedica. Se la risposta non è esplicitamente o \
implicitamente desumibile dal materiale fornito, imposta trovata=false e \
confidenza bassa.

Per ogni domanda a risposta multipla:
1. Cerca nel materiale le informazioni rilevanti per la domanda
2. Identifica l'opzione corretta basandoti SOLO sul materiale
3. q_key: scegli 2-3 parole DISTINTIVE della domanda (quelle che la identificano \
   univocamente rispetto alle altre domande dell'esame)
4. risposta: scegli 2-3 parole DISTINTIVE dell'opzione corretta (NON le lettere A/B/C/D)
5. confidenza: 1.0 = citazione diretta nel materiale; 0.7 = inferenza chiara; \
   0.4 = inferenza debole; 0.1 = non trovato
6. Chiama lo strumento risposta_domanda con tutti i campi compilati
"""

# System prompt per il backend Ollama (JSON puro, no tool use)
SYSTEM_OLLAMA = """\
Sei un assistente per esami universitari italiani.

REGOLA FONDAMENTALE: Rispondi ESCLUSIVAMENTE in base ai BRANI DEL MATERIALE \
riportati nel messaggio dell'utente. NON usare la tua conoscenza generale.
Se la risposta non è deducibile dal materiale, imposta trovata=false e confidenza bassa.

Rispondi SEMPRE con un oggetto JSON valido con ESATTAMENTE questi campi:
{
  "q_key": "<2-3 parole distintive della domanda>",
  "risposta": "<2-3 parole distintive dell'opzione corretta>",
  "opzione": "<A, B, C o D>",
  "confidenza": <numero 0.0-1.0>,
  "trovata": <true o false>
}

Regole:
- q_key: parole che identificano univocamente la domanda (no "qual è", no "che cosa")
- risposta: parole distinctive dell'opzione corretta (no "la risposta è")
- opzione: SOLO la lettera maiuscola A, B, C o D
- confidenza: 1.0=citazione diretta; 0.7=inferenza chiara; 0.4=debole; 0.1=non trovato
- trovata: true se la risposta è nel materiale, false altrimenti

NON aggiungere testo fuori dal JSON. NON usare ```json. Solo il JSON puro.
"""

ANSWER_TOOL = {
    "name": "risposta_domanda",
    "description": "Restituisce la risposta a una domanda a risposta multipla, fondata sul materiale didattico.",
    "input_schema": {
        "type": "object",
        "properties": {
            "q_key": {
                "type": "string",
                "description": "2-3 parole più distintive della domanda"
            },
            "risposta": {
                "type": "string",
                "description": "2-3 parole più distintive dell'opzione corretta"
            },
            "opzione": {
                "type": "string",
                "enum": ["A", "B", "C", "D"],
                "description": "Lettera dell'opzione corretta"
            },
            "confidenza": {
                "type": "number",
                "description": "Confidenza nella risposta: 0.0 (non trovata) – 1.0 (certezza)"
            },
            "trovata": {
                "type": "boolean",
                "description": "true se la risposta è esplicitamente o implicitamente nel materiale"
            }
        },
        "required": ["q_key", "risposta", "opzione", "confidenza", "trovata"]
    }
}

# System prompt per il fallback Ollama di segmentazione (Stage 2.5)
SYSTEM_SEGMENTA = """\
Sei un assistente che analizza testo OCR di screenshot di esami universitari italiani.

Il testo contiene UNA O PIÙ domande a risposta multipla. Il tuo compito è separarle.

Rispondi SOLO con un oggetto JSON valido:
{"domande": ["<testo domanda 1 con le sue opzioni>", "<testo domanda 2 con le sue opzioni>", ...]}

Regole:
- Ogni elemento è una stringa con il testo di UNA sola domanda e le sue opzioni di risposta.
- Copia il testo verbatim dall'OCR: NON correggere, NON parafrasare.
- Se c'è una sola domanda, la lista ha un solo elemento.
- NON aggiungere testo fuori dal JSON. NON usare ```json. Solo il JSON puro.
"""


# ─── Stage 1: Knowledge base ──────────────────────────────────────────────────

def estrai_flashcard_ecologia(html_path: Path) -> str:
    """Estrae le coppie {q, a} dal blocco <script> di quizecologia/index.html."""
    testo = html_path.read_text(encoding="utf-8")
    # Gestisce sia virgolette doppie che singole, spazi variabili
    pattern = r'\{\s*q:\s*["\']([^"\']+)["\']\s*,\s*a:\s*["\']([^"\']+)["\']\s*\}'
    coppie = re.findall(pattern, testo)
    if not coppie:
        return ""
    righe = [f"D: {q}\nR: {a}" for q, a in coppie]
    return "## Flashcard ecologia\n\n" + "\n\n".join(righe)


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
        print(f"    ⚠ pdftotext non trovato — installa poppler-utils", flush=True)
        return ""
    except subprocess.TimeoutExpired:
        print(f"    ⚠ timeout nell'estrazione di {pdf_path.name}", flush=True)
        return ""

    if not testo:
        print(f"    ⚠ nessun testo estratto da {pdf_path.name} (PDF scansionato?)", flush=True)
        return ""

    contenuto = f"## {pdf_path.stem}\n\n{testo}"
    cache_path.write_text(contenuto, encoding="utf-8")
    parole = len(testo.split())
    print(f"    ✓ estratto {pdf_path.name}: {parole:,} parole → cache {cache_path.name}", flush=True)
    return contenuto


def _fingerprint_blocco(testo: str) -> str:
    """
    Calcola un fingerprint leggero del contenuto per rilevare duplicati.
    Normalizza: minuscolo, watermark Studocu rimossi, spazi collassati,
    poi fa SHA-256 dei primi 3000 caratteri.
    """
    normalizzato = testo.lower()
    normalizzato = re.sub(r"lOMoARcPSD\|[\w]+", "", normalizzato)  # watermark Studocu
    normalizzato = re.sub(r"\s+", " ", normalizzato).strip()
    campione = normalizzato[:3000]
    return hashlib.sha256(campione.encode("utf-8")).hexdigest()


def costruisci_knowledge_base(materia_path: Path) -> str:
    """
    Costruisce la knowledge base dalla cartella della materia.
    Ordine di priorità: flashcard HTML > recap .md (nomi con ripasso/recap/completo/
    riepilogo/comprensiv) > altri .md > fallback PDF.
    I duplicati (stesso contenuto con nomi diversi) vengono saltati.
    """
    blocchi = []
    fingerprints_visti: set[str] = set()

    def _aggiungi_se_nuovo(etichetta: str, testo: str, blocco: str) -> bool:
        """Aggiunge il blocco solo se non è un duplicato. Ritorna True se aggiunto."""
        fp = _fingerprint_blocco(testo)
        if fp in fingerprints_visti:
            print(f"    ⊘ {etichetta} saltato (duplicato)", flush=True)
            return False
        fingerprints_visti.add(fp)
        blocchi.append(blocco)
        print(f"    ✓ {etichetta}: {len(testo.split()):,} parole", flush=True)
        return True

    # Caso speciale: quizecologia (flashcard inline in index.html)
    html_ecologia = materia_path / "index.html"
    if html_ecologia.exists():
        fc = estrai_flashcard_ecologia(html_ecologia)
        if fc:
            _aggiungi_se_nuovo("flashcard ecologia", fc, fc)

    # File .md (esclude i .extracted.md generati da estrai_pdf)
    md_files = sorted(
        p for p in materia_path.glob("*.md")
        if not p.name.endswith(".extracted.md")
    )
    md_stems = {p.stem for p in md_files}

    # Partiziona: recap comprensivi (per RECAP_KEYWORDS) caricati per primi
    recap_files = [p for p in md_files if any(k in p.stem.lower() for k in RECAP_KEYWORDS)]
    altri_md    = [p for p in md_files if not any(k in p.stem.lower() for k in RECAP_KEYWORDS)]
    if recap_files:
        print(f"    ↳ {len(recap_files)} file recap caricati per primi: {', '.join(p.name for p in recap_files)}", flush=True)

    for md_path in recap_files + altri_md:
        testo = md_path.read_text(encoding="utf-8")
        _aggiungi_se_nuovo(md_path.name, testo, f"## FILE: {md_path.name}\n\n{testo}")

    # Fallback PDF: processa i PDF senza .md omonimo
    for pdf_path in sorted(materia_path.glob("*.pdf")):
        if pdf_path.stem in md_stems:
            continue  # Esiste già un .md con lo stesso nome, ha priorità
        estratto = estrai_pdf(pdf_path)
        if estratto:
            # Il testo grezzo del PDF è estratto; usiamo il blocco estratto come
            # testo per il fingerprint (escludiamo l'intestazione ## ...)
            testo_grezzo = estratto.split("\n\n", 2)[-1] if "\n\n" in estratto else estratto
            _aggiungi_se_nuovo(pdf_path.name, testo_grezzo, estratto)

    if not blocchi:
        print("  ⚠ Nessun materiale trovato nella cartella della materia!", flush=True)
        sys.exit(1)

    kb = "\n\n---\n\n".join(blocchi)
    parole_tot = len(kb.split())
    token_stimati = parole_tot // 750 * 1000  # ~750 parole/1k token IT
    print(f"\n    Knowledge base totale: {parole_tot:,} parole (~{token_stimati//1000}k token stimati)", flush=True)
    if parole_tot > 140_000:
        print("    ⚠ Knowledge base molto grande — potrebbero verificarsi errori di contesto", flush=True)
    return kb


# ─── Stage 2: OCR ─────────────────────────────────────────────────────────────

def _ocr_singolo(img_path: Path) -> str:
    """OCR su una singola immagine. Ritorna il testo estratto."""
    img = Image.open(img_path)

    # Converti in scala di grigi (migliora l'accuratezza Tesseract)
    if img.mode != "L":
        img = img.convert("L")

    # Upscale se l'immagine è troppo piccola (Tesseract funziona meglio a ~150–300 DPI)
    w, h = img.size
    if w < 1400:
        scale = 1400 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    testo = pytesseract.image_to_string(img, lang="ita", config="--psm 6")
    return testo.strip()


def ocr_parallelo(immagini: list[Path], workers: int) -> list[tuple[int, Path, str]]:
    """OCR parallelo su tutte le immagini. Stampa avanzamento; ritorna lista ordinata per indice."""
    risultati: list[tuple[int, Path, str]] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_ocr_singolo, p): (i, p) for i, p in enumerate(immagini)}
        completati = 0
        for fut in as_completed(futures):
            i, p = futures[fut]
            completati += 1
            try:
                testo = fut.result()
                risultati.append((i, p, testo))
                preview = testo[:60].replace("\n", " ")
                print(f"    [{completati:02d}/{len(immagini)}] {p.name} → \"{preview}…\"", flush=True)
            except Exception as e:
                print(f"    ⚠ OCR fallito per {p.name}: {e}", flush=True)
                risultati.append((i, p, f"[OCR FALLITO: {e}]"))

    risultati.sort(key=lambda x: x[0])
    return risultati


# ─── Stage 2.5: Segmentazione domande ─────────────────────────────────────────

# Pattern riutilizzati in più funzioni di segmentazione
_RE_GLIFO   = re.compile(r'^[Î>}|■►●]\s')  # marcatore domanda (layout grammatica)
_RE_OPZ_O   = re.compile(r'^[OoQ0©]\s+\S')          # opzione cerchietto (grammatica; © = OCR radio button)
_RE_OPZ_LET = re.compile(r'^[A-Dpcb]{1}[.)\s]\s*\S') # opzione lettera A/B/C/D (didattica)
_RE_RUMORE  = re.compile(                            # righe da ignorare
    r'^(?:e{2,}|[-=_+/*]{3,}|domanda\s+\d+\s+di\s+\d+)$', re.I
)


def _is_opzione_riga(riga: str) -> bool:
    return bool(_RE_OPZ_O.match(riga) or _RE_OPZ_LET.match(riga))


def _pulisci_riga(riga: str) -> str:
    """Rimuove il marcatore iniziale (Î, O, A., ecc.) da una riga OCR."""
    riga = _RE_GLIFO.sub('', riga)
    riga = re.sub(r'^[OoQ0]\s+', '', riga)
    riga = re.sub(r'^[A-Dpcb]{1}[.)\s]\s*', '', riga)
    return riga.strip()


def _segmenta_euristico(testo: str) -> list[str]:
    """
    Spezza il testo OCR di un'immagine in blocchi-domanda distinti.

    Strategia 1 (layout grammatica — marcatore Î presente):
        Ogni riga che inizia con 'Î' apre un nuovo blocco. Caso comune per
        quizgrammatica, dove ogni screenshot ha ~3 domande impilate.

    Strategia 2 (layout senza Î — es. quizdidattica):
        Split sulla transizione opzione→non-opzione, solo dopo ≥ 3 opzioni
        nel blocco corrente. Evita falsi split su righe di wrap/continuazione.
    """
    righe = [r.strip() for r in testo.splitlines()
             if r.strip() and not _RE_RUMORE.match(r.strip())]
    if not righe:
        return [testo.strip()] if testo.strip() else []

    usa_glifo = any(_RE_GLIFO.match(r) for r in righe)

    # I blocchi vengono costruiti con le righe ORIGINALI (non pulite) per poter
    # eseguire correttamente _is_opzione_riga nel post-processing. La pulizia
    # dei marcatori avviene solo al momento di produrre l'output.
    blocchi_raw: list[list[str]] = []
    corrente: list[str] = []

    if usa_glifo:
        # Strategia 1: split esplicito sul glifo Î
        for riga in righe:
            if _RE_GLIFO.match(riga) and corrente:
                blocchi_raw.append(corrente)
                corrente = []
            corrente.append(riga)
    else:
        # Strategia 2: split sulla transizione opzione→non-opzione.
        # Condizioni: ≥ 4 opzioni viste (evita split dopo solo 3 su immagini con wrap)
        # E la riga non-opzione deve avere ≥ 4 parole (esclude righe di continuazione
        # come "alla lingua" o "loro lingua" che sono tail di un'opzione wrappata).
        MIN_OPZ = 4
        MIN_PAROLE_Q = 4
        opz_in_blocco = 0
        ultima_era_opzione = False
        for riga in righe:
            e_opzione = _is_opzione_riga(riga)
            if (not e_opzione and ultima_era_opzione
                    and opz_in_blocco >= MIN_OPZ
                    and len(riga.split()) >= MIN_PAROLE_Q
                    and corrente):
                blocchi_raw.append(corrente)
                corrente = []
                opz_in_blocco = 0
            corrente.append(riga)
            if e_opzione:
                opz_in_blocco += 1
            ultima_era_opzione = e_opzione

    if corrente:
        blocchi_raw.append(corrente)

    # Post-processing: i blocchi senza opzioni (righe di continuazione / wrap)
    # vengono fusi nel blocco precedente invece di diventare domande separate.
    # Confronto sulle righe ORIGINALI (prima della pulizia dei marcatori).
    blocchi_finali: list[list[str]] = []
    for b in blocchi_raw:
        ha_opzioni = any(_is_opzione_riga(r) for r in b)
        if not ha_opzioni and blocchi_finali:
            blocchi_finali[-1].extend(b)
        else:
            blocchi_finali.append(b)

    # Pulizia dei marcatori e join finale
    risultato = [
        '\n'.join(_pulisci_riga(r) for r in b if r.strip()).strip()
        for b in blocchi_finali
    ]
    risultato = [t for t in risultato if t]
    return risultato if risultato else [testo.strip()]


def _split_sospetto(blocchi: list[str], testo_originale: str) -> bool:
    """
    Ritorna True se il risultato euristico sembra inaffidabile e vale la pena
    invocare il fallback Ollama.

    Il rapporto opzioni/blocco è calcolato SOLO sui blocchi che contengono
    almeno un'opzione (i blocchi di continuazione sono già stati fusi).

    Criteri di sospetto:
    - 0 blocchi con opzioni
    - 1 blocco effettivo con ≥ 8 opzioni (= 2+ domande probabilmente fuse)
    - rapporto opzioni/blocco < 2.5  (split troppo aggressivo)
    - rapporto opzioni/blocco ≥ 5.5  (domande probabilmente ancora fuse)
    """
    B = len(blocchi)
    if B == 0:
        return True

    # Conta le righe-opzione nel testo originale (riga per riga, non regex multiline)
    # Il post-processing in _segmenta_euristico ha già fuso i blocchi di continuazione,
    # quindi B riflette correttamente il numero di domande estratte.
    M = sum(1 for r in testo_originale.splitlines() if _is_opzione_riga(r.strip()))
    if M < 2:
        return False  # Testo libero o OCR vuoto — nessun fallback utile

    if B == 1 and M >= 8:
        return True   # 1 blocco, 8+ opzioni → 2+ domande probabilmente fuse

    rapporto = M / B
    return rapporto < 2.5 or rapporto >= 5.5


def _segmenta_ollama(ollama_mod, model: str, testo: str) -> list[str]:
    """
    Usa il modello Ollama locale per separare domande multiple in un testo OCR.
    Chiamato solo come fallback quando _split_sospetto() ritorna True.
    Ritorna [testo] se il parsing JSON fallisce (per non perdere domande).
    """
    try:
        response = ollama_mod.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_SEGMENTA},
                {"role": "user",   "content": f"Testo OCR da separare:\n\n{testo}"}
            ],
            format="json",
            options={"num_ctx": 4096, "temperature": 0}
        )
        raw = response.message.content.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        dati = json.loads(raw)
        domande = dati.get("domande", [])
        if isinstance(domande, list) and all(isinstance(d, str) for d in domande):
            pulite = [d.strip() for d in domande if d.strip()]
            return pulite if pulite else [testo]
    except Exception:
        pass
    return [testo]


def segmenta_domande(
    ocr_results: list[tuple[int, Path, str]],
    ollama_mod,
    model: str
) -> list[tuple[int, Path, str]]:
    """
    Stage 2.5 — Segmentazione: spezza ogni testo OCR in singole domande.

    Per ogni immagine:
      1. Prova lo splitter euristico (istantaneo, nessuna chiamata LLM).
      2. Se il risultato sembra incoerente, usa il modello Ollama come fallback.
      3. Stampa avanzamento.

    Ritorna una lista piatta di tuple (qid, path, testo_domanda) con qid
    sequenziale globale — stessa forma di ocr_results, compatibile con
    risposte_ollama_rag() e risposte_parallele() senza modifiche.
    """
    lista_piatta: list[tuple[int, Path, str]] = []
    qid = 0

    for _i, path, testo in ocr_results:
        blocchi = _segmenta_euristico(testo)

        usato_fallback = False
        if ollama_mod is not None and _split_sospetto(blocchi, testo):
            blocchi_fb = _segmenta_ollama(ollama_mod, model, testo)
            if blocchi_fb:
                blocchi = blocchi_fb
                usato_fallback = True

        k = len(blocchi)
        fb_label = "  (fallback ollama)" if usato_fallback else ""
        print(f"    {path.name} → {k} domand{'e' if k != 1 else 'a'}{fb_label}", flush=True)

        for blocco in blocchi:
            lista_piatta.append((qid, path, blocco))
            qid += 1

    return lista_piatta


# ─── Stage 3a: Claude API con prompt caching ──────────────────────────────────

def build_system_blocks(kb: str) -> list:
    """
    Costruisce i blocchi del system prompt.
    Il blocco MATERIALE è marcato con cache_control ephemeral:
    viene messo in cache dalla prima domanda e riusato da tutte le successive.
    """
    return [
        {
            "type": "text",
            "text": SYSTEM_ISTRUZIONI
        },
        {
            "type": "text",
            "text": f"MATERIALE DIDATTICO:\n\n{kb}",
            "cache_control": {"type": "ephemeral"}
        }
    ]


def _rispondi_singola(
    client,
    model: str,
    system_blocks: list,
    idx: int,
    testo_ocr: str
) -> dict:
    """
    Chiama Claude API per una domanda. Tool use forzato → JSON strutturato.
    Il system con cache_control viene messo in cache alla prima chiamata.
    Retry automatico con backoff esponenziale su rate limit (429/529).
    """
    ritardi = [2, 4, 8, 16, 32, 60]  # secondi tra i tentativi

    for tentativo, ritardo in enumerate(ritardi + [None]):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=256,
                system=system_blocks,
                tools=[ANSWER_TOOL],
                tool_choice={"type": "tool", "name": "risposta_domanda"},
                messages=[{
                    "role": "user",
                    "content": f"Domanda {idx + 1:02d}:\n\n{testo_ocr}"
                }]
            )
            for block in resp.content:
                if block.type == "tool_use":
                    return block.input
            return _errore_risposta(idx, "nessun tool_use nel response")

        except anthropic.APIConnectionError as e:
            return _errore_risposta(idx, f"connessione fallita: {e}")

        except anthropic.RateLimitError as e:
            if ritardo is None:
                return _errore_risposta(idx, f"rate limit: tentativi esauriti")
            # Rispetta l'header Retry-After se presente
            retry_after = None
            try:
                retry_after = int(e.response.headers.get("retry-after", 0))
            except Exception:
                pass
            attesa = max(ritardo, retry_after or 0)
            print(f"    ⏳ [{idx + 1:02d}] rate limit (tentativo {tentativo + 1}), attesa {attesa}s…", flush=True)
            time.sleep(attesa)

        except anthropic.APIStatusError as e:
            # 529 = overloaded; trattato come rate limit
            if e.status_code in (429, 529) and ritardo is not None:
                retry_after = None
                try:
                    retry_after = int(e.response.headers.get("retry-after", 0))
                except Exception:
                    pass
                attesa = max(ritardo, retry_after or 0)
                print(f"    ⏳ [{idx + 1:02d}] API {e.status_code} (tentativo {tentativo + 1}), attesa {attesa}s…", flush=True)
                time.sleep(attesa)
            else:
                return _errore_risposta(idx, f"API error {e.status_code}: {e.message}")

        except Exception as e:
            return _errore_risposta(idx, str(e))

    return _errore_risposta(idx, "tentativi esauriti")


# ─── Formattazione condivisa ───────────────────────────────────────────────────

def _errore_risposta(idx: int, msg: str) -> dict:
    return {
        "q_key": f"domanda {idx + 1}",
        "risposta": msg,
        "opzione": "A",
        "confidenza": 0.0,
        "trovata": False
    }


def _formatta_riga(i: int, testo: str, risposta: dict) -> tuple[str, str, dict]:
    """Formatta una riga compatta e la stampa."""
    q_key   = risposta.get("q_key", "?")
    ans     = risposta.get("risposta", "?")
    opzione = risposta.get("opzione", "?")
    conf    = float(risposta.get("confidenza", 0.0))
    trovata = bool(risposta.get("trovata", False))

    if trovata:
        riga = f'[{i + 1:02d}] {q_key} → "{ans}" ({opzione})  ✓{conf:.2f}'
    else:
        riga = f'[{i + 1:02d}] {q_key} → {ans} ({opzione})  ✗{conf:.2f}  ⚠ non nel materiale'

    print(riga, flush=True)
    return (riga, testo, risposta)


def risposte_parallele(
    client,
    model: str,
    system_blocks: list,
    ocr_results: list[tuple[int, Path, str]],
    workers: int
) -> list[tuple[str, str, dict] | None]:
    """
    Chiamate API con cache warming + parallelo.

    Step 1 (sincrono): esegue la PRIMA domanda da sola per scrivere la cache
    ephemeral nel sistema Anthropic prima che le altre partano.

    Step 2 (parallelo): le domande rimanenti vengono inviate tutte in parallelo;
    a quel punto la cache è già calda e ognuna pagherà solo cache_read_input_tokens.

    Stampa ogni riga compatta APPENA disponibile.
    Ritorna output_lines ordinata per indice (per il file di salvataggio).
    """
    n = len(ocr_results)
    output_lines: list[tuple[str, str, dict] | None] = [None] * n

    if n == 0:
        return output_lines

    # ── Step 1: cache warming (prima domanda, sincrona) ─────────────────────
    print("  → Riscaldo la cache (domanda 01)…", flush=True)
    i0, path0, testo0 = ocr_results[0]
    risposta0 = _rispondi_singola(client, model, system_blocks, i0, testo0)
    output_lines[i0] = _formatta_riga(i0, testo0, risposta0)

    if n == 1:
        return output_lines

    # ── Step 2: restanti in parallelo (cache già scritta) ───────────────────
    print(f"  → {n - 1} domande in parallelo (cache calda)…", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(_rispondi_singola, client, model, system_blocks, i, testo): (i, path, testo)
            for i, path, testo in ocr_results[1:]
        }

        for fut in as_completed(futures):
            i, path, testo = futures[fut]
            risposta = fut.result()
            output_lines[i] = _formatta_riga(i, testo, risposta)

    return output_lines


# ─── Stage 3b: Ollama RAG ─────────────────────────────────────────────────────

def chunk_kb(kb: str, finestra: int = 150, overlap: int = 30) -> list[str]:
    """
    Spezza la knowledge base in chunk con overlap per il RAG.

    Split primario sui separatori di blocco già presenti nella KB
    (\n\n---\n\n), secondario sulle intestazioni ## . Poi sub-chunk a
    finestra scorrevole (finestra parole, overlap parole di sovrapposizione)
    così ogni brano rimane autocontenuto e le frasi a cavallo vengono
    rappresentate in entrambi i chunk.
    """
    def _sub_chunk(testo: str) -> list[str]:
        parole = testo.split()
        if not parole:
            return []
        if len(parole) <= finestra:
            return [testo.strip()]
        chunks = []
        start = 0
        while start < len(parole):
            fine = min(start + finestra, len(parole))
            chunks.append(" ".join(parole[start:fine]))
            if fine == len(parole):
                break
            start += finestra - overlap
        return chunks

    risultati = []
    for blocco in kb.split("\n\n---\n\n"):
        if not blocco.strip():
            continue
        for sezione in re.split(r'\n(?=## )', blocco):
            if sezione.strip():
                risultati.extend(_sub_chunk(sezione))
    return risultati


def embedda_chunks(
    ollama_mod,
    embed_model: str,
    kb: str,
    chunks: list[str]
) -> "np.ndarray":
    """
    Embedda tutti i chunk con il modello specificato.

    La matrice (N, D) viene salvata in esame/.cache/emb_<hash16>.npz e
    riusata alle esecuzioni successive. La cache è invalidata automaticamente
    se il contenuto del materiale o il nome del modello cambiano.
    """
    chiave = hashlib.sha256(f"{kb}||{embed_model}".encode()).hexdigest()[:16]
    cache_dir = Path(__file__).parent / ".cache"
    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / f"emb_{chiave}.npz"

    if cache_path.exists():
        print(f"    [cache] {cache_path.name}", flush=True)
        return np.load(cache_path)["embeddings"]

    print(f"    Embedding di {len(chunks)} chunk con {embed_model}…", flush=True)
    try:
        # API batch (ollama >= 0.3.x)
        risposta = ollama_mod.embed(model=embed_model, input=chunks)
        embs = np.array(risposta.embeddings, dtype=np.float32)
    except Exception as e:
        # Fallback: API singola (versioni ollama più vecchie)
        print(f"    ⚠ embed batch fallito ({e}), uso fallback singolo…", flush=True)
        lista = []
        for j, chunk in enumerate(chunks):
            r = ollama_mod.embeddings(model=embed_model, prompt=chunk)
            lista.append(r["embedding"])
            if (j + 1) % 20 == 0:
                print(f"    [{j+1}/{len(chunks)}]", flush=True)
        embs = np.array(lista, dtype=np.float32)

    np.savez_compressed(cache_path, embeddings=embs)
    print(f"    ✓ cache salvata: {cache_path.name}", flush=True)
    return embs


def recupera(
    query_emb: "np.ndarray",
    chunk_embs: "np.ndarray",
    chunks: list[str],
    k: int
) -> list[str]:
    """Similarità coseno: ritorna i top-k chunk più pertinenti alla query."""
    q = query_emb / (np.linalg.norm(query_emb) + 1e-9)
    c = chunk_embs / (np.linalg.norm(chunk_embs, axis=1, keepdims=True) + 1e-9)
    scores = c @ q
    top_idx = np.argsort(scores)[::-1][:k]
    return [chunks[i] for i in top_idx]


def _rispondi_ollama(
    ollama_mod,
    model: str,
    embed_model: str,
    chunk_embs: "np.ndarray",
    chunks: list[str],
    idx: int,
    testo_ocr: str,
    top_k: int
) -> dict:
    """
    Risponde a una singola domanda con Ollama + RAG.
    Embedda la domanda, recupera i top-k brani più pertinenti,
    chiama ollama.chat con format="json" e valida il risultato.
    """
    # 1. Embedding della domanda
    try:
        q_resp = ollama_mod.embed(model=embed_model, input=[testo_ocr])
        q_emb = np.array(q_resp.embeddings[0], dtype=np.float32)
    except Exception as e:
        try:
            r = ollama_mod.embeddings(model=embed_model, prompt=testo_ocr)
            q_emb = np.array(r["embedding"], dtype=np.float32)
        except Exception as e2:
            return _errore_risposta(idx, f"embedding query fallito: {e2}")

    # 2. Recupero dei brani pertinenti
    brani = recupera(q_emb, chunk_embs, chunks, top_k)
    materiale = "\n\n".join(f"[Brano {j+1}]\n{b}" for j, b in enumerate(brani))

    # 3. Risposta via Ollama
    messaggio_utente = (
        f"MATERIALE PERTINENTE:\n\n{materiale}\n\n"
        f"---\n\nDomanda {idx + 1:02d}:\n\n{testo_ocr}"
    )
    try:
        response = ollama_mod.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_OLLAMA},
                {"role": "user",   "content": messaggio_utente}
            ],
            format="json",
            options={"num_ctx": 8192, "temperature": 0}
        )
        testo = response.message.content.strip()

        # Rimuovi eventuale wrapper ```json ... ``` prodotto da modelli che
        # ignorano l'istruzione "solo JSON puro"
        testo = re.sub(r"^```(?:json)?\s*", "", testo)
        testo = re.sub(r"\s*```$", "", testo)

        dati = json.loads(testo)

        # Validazione e normalizzazione campi
        for campo in ("q_key", "risposta", "opzione", "confidenza", "trovata"):
            if campo not in dati:
                raise ValueError(f"campo mancante: {campo!r}")
        dati["opzione"] = str(dati["opzione"]).upper().strip()
        if dati["opzione"] not in ("A", "B", "C", "D"):
            dati["opzione"] = "A"
        dati["confidenza"] = float(dati["confidenza"])
        dati["trovata"]    = bool(dati["trovata"])
        return dati

    except Exception as e:
        return _errore_risposta(idx, f"ollama errore: {e}")


def _verifica_ollama(ollama_mod, model: str, embed_model: str) -> None:
    """Verifica che il server Ollama risponda e che i modelli necessari siano disponibili."""
    try:
        lista = ollama_mod.list()
        modelli_presenti = {m.model for m in lista.models}
    except Exception as e:
        print(f"✗ Ollama non raggiungibile: {e}", file=sys.stderr)
        print("  Assicurati che ollama sia in esecuzione:", file=sys.stderr)
        print("    ollama serve", file=sys.stderr)
        sys.exit(1)

    mancanti = []
    for nome in (model, embed_model):
        # ollama list riporta il tag completo (es. "qwen2.5:7b"); accetta anche senza tag
        if nome not in modelli_presenti and f"{nome}:latest" not in modelli_presenti:
            mancanti.append(nome)

    if mancanti:
        for nome in mancanti:
            print(f"✗ Modello Ollama non trovato: {nome}", file=sys.stderr)
            print(f"  Installa con: ollama pull {nome}", file=sys.stderr)
        sys.exit(1)


def risposte_ollama_rag(
    ollama_mod,
    model: str,
    embed_model: str,
    kb: str,
    ocr_results: list[tuple[int, Path, str]],
    top_k: int,
    workers: int
) -> list:
    """
    Orchestratore Stage 3b: embedding dei chunk (con cache) + risposte RAG.

    I chunk vengono embeddati una sola volta (con cache su disco) e poi
    per ogni domanda si recuperano i top-k brani più pertinenti via
    similarità coseno. Il parallelismo è limitato per non saturare la RAM
    con più slot del modello locale in contemporanea.
    Output in tempo reale identico al backend Claude.
    """
    n = len(ocr_results)
    output_lines: list = [None] * n

    if n == 0:
        return output_lines

    # Chunk + embedding (una sola volta, con cache automatica)
    print("  → Chunking del materiale…", flush=True)
    chunks = chunk_kb(kb)
    print(f"    {len(chunks)} chunk generati", flush=True)

    print(f"  → Embedding chunk ({embed_model})…", flush=True)
    chunk_embs = embedda_chunks(ollama_mod, embed_model, kb, chunks)
    print(f"    ✓ {chunk_embs.shape[0]} vettori ({chunk_embs.shape[1]}d)\n", flush=True)

    # Risposte: sequenziale se workers=1, parallelo altrimenti
    if workers <= 1:
        for i, _path, testo in ocr_results:
            risposta = _rispondi_ollama(
                ollama_mod, model, embed_model, chunk_embs, chunks, i, testo, top_k
            )
            output_lines[i] = _formatta_riga(i, testo, risposta)
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {
                ex.submit(
                    _rispondi_ollama,
                    ollama_mod, model, embed_model, chunk_embs, chunks, i, testo, top_k
                ): (i, _path, testo)
                for i, _path, testo in ocr_results
            }
            for fut in as_completed(futures):
                i, _path, testo = futures[fut]
                risposta = fut.result()
                output_lines[i] = _formatta_riga(i, testo, risposta)

    return output_lines


# ─── Stage 4: Salva risultati ──────────────────────────────────────────────────

def salva_risultati(
    output_lines: list,
    materia_path: Path,
    immagini_path: Path,
    model_name: str
) -> Path:
    """Salva i risultati completi (OCR + risposta) in un file markdown."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = Path(__file__).parent  # cartella esame/
    out_path = out_dir / f"risultati_{timestamp}.md"

    righe = [
        f"# Risultati esame — {timestamp}",
        f"",
        f"- **Materia**: `{materia_path}`",
        f"- **Immagini**: `{immagini_path}`",
        f"- **Modello**: `{model_name}`",
        f"",
        "---",
        "",
    ]

    for item in output_lines:
        if item is None:
            continue
        riga_compatta, testo_ocr, risposta = item

        righe.append(f"## {riga_compatta}")
        righe.append("")
        righe.append("**Testo OCR:**")
        righe.append("```")
        ocr_preview = testo_ocr[:800] + ("…" if len(testo_ocr) > 800 else "")
        righe.append(ocr_preview)
        righe.append("```")
        righe.append("")
        righe.append(f"| Campo | Valore |")
        righe.append(f"|---|---|")
        righe.append(f"| Opzione | **{risposta.get('opzione', '?')}** |")
        righe.append(f"| Risposta | {risposta.get('risposta', '?')} |")
        righe.append(f"| Confidenza | {float(risposta.get('confidenza', 0)):.2f} |")
        righe.append(f"| Nel materiale | {'✓' if risposta.get('trovata') else '✗'} |")
        righe.append("")

    out_path.write_text("\n".join(righe), encoding="utf-8")
    return out_path


# ─── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Risolutore domande d'esame: OCR locale + LLM con grounding sui materiali.\n"
            "Backend --backend claude (default) usa l'API Anthropic.\n"
            "Backend --backend ollama usa un modello locale via Ollama (gratuito, offline)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--immagini", required=True, type=Path,
        help="Cartella con le immagini delle domande (.png, .jpg, …)"
    )
    parser.add_argument(
        "--materia", required=True, type=Path,
        help="Cartella con i materiali di studio (.md, .pdf, index.html)"
    )
    parser.add_argument(
        "--backend", choices=["claude", "ollama"], default="claude",
        help="Backend LLM: claude (default, API Anthropic) o ollama (locale, gratuito)"
    )
    parser.add_argument(
        "--modello", default=None,
        help=(
            "Modello da usare. Per Claude: 'haiku' (default) o 'sonnet'. "
            "Per Ollama: nome del modello Ollama (default: qwen2.5:7b)"
        )
    )
    parser.add_argument(
        "--embed-modello", default=OLLAMA_EMBED_DEFAULT, dest="embed_modello",
        help=f"[Ollama] Modello embedding per il RAG (default: {OLLAMA_EMBED_DEFAULT})"
    )
    parser.add_argument(
        "--top-k", type=int, default=6, dest="top_k",
        help="[Ollama] Numero di brani recuperati per domanda nel RAG (default: 6)"
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help=(
            "Thread paralleli per OCR e API (default: 8). "
            "Per Ollama viene automaticamente limitato a 2 per risparmiare RAM."
        )
    )
    args = parser.parse_args()

    # ── Validazione input comune ─────────────────────────────────────────────
    if not args.immagini.is_dir():
        print(f"✗ Cartella immagini non trovata: {args.immagini}", file=sys.stderr)
        sys.exit(1)
    if not args.materia.is_dir():
        print(f"✗ Cartella materia non trovata: {args.materia}", file=sys.stderr)
        sys.exit(1)

    # ── Configurazione backend ───────────────────────────────────────────────
    if args.backend == "claude":
        if anthropic is None:
            print("✗ Libreria 'anthropic' non installata.", file=sys.stderr)
            print("  pip install anthropic", file=sys.stderr)
            sys.exit(1)
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("✗ ANTHROPIC_API_KEY non impostata nell'ambiente", file=sys.stderr)
            print("  export ANTHROPIC_API_KEY=sk-ant-…", file=sys.stderr)
            sys.exit(1)
        modello_scelto = args.modello or "haiku"
        if modello_scelto not in MODELLI_CLAUDE:
            print(f"✗ Modello Claude non riconosciuto: {modello_scelto!r}", file=sys.stderr)
            print(f"  Valori validi: {list(MODELLI_CLAUDE)}", file=sys.stderr)
            sys.exit(1)
        model = MODELLI_CLAUDE[modello_scelto]

    else:  # ollama
        if ollama is None:
            print("✗ Libreria 'ollama' non installata.", file=sys.stderr)
            print("  pip install ollama", file=sys.stderr)
            sys.exit(1)
        modello_scelto = args.modello or OLLAMA_MODELLO_DEFAULT
        model = modello_scelto
        _verifica_ollama(ollama, model, args.embed_modello)

    # ── Raccolta immagini ─────────────────────────────────────────────────────
    immagini = sorted(
        p for p in args.immagini.iterdir()
        if p.is_file() and p.suffix.lower() in IMG_EXTENSIONS
    )
    if not immagini:
        print(f"✗ Nessuna immagine trovata in {args.immagini}", file=sys.stderr)
        print(f"  Estensioni supportate: {', '.join(sorted(IMG_EXTENSIONS))}", file=sys.stderr)
        sys.exit(1)

    # ── Header ───────────────────────────────────────────────────────────────
    backend_label = f"{args.backend}:{model}"
    if args.backend == "ollama":
        backend_label += f"  embed:{args.embed_modello}  top-k:{args.top_k}"
    ollama_workers = min(args.workers, 2) if args.backend == "ollama" else args.workers

    print()
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  risolvi.py                                                  ║")
    print(f"║  {len(immagini):2d} immagini  ·  {backend_label}".ljust(63) + "║")
    print(f"║  {ollama_workers} workers".ljust(63) + "║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print()

    t0 = time.time()

    # ── Stage 1: Knowledge base ──────────────────────────────────────────────
    print("▶ Stage 1 — Knowledge base")
    kb = costruisci_knowledge_base(args.materia)
    print(f"  ✓ completato in {time.time() - t0:.1f}s\n")

    # ── Stage 2: OCR ─────────────────────────────────────────────────────────
    t1 = time.time()
    print(f"▶ Stage 2 — OCR ({len(immagini)} immagini, {args.workers} workers)")
    ocr_results = ocr_parallelo(immagini, args.workers)
    print(f"  ✓ completato in {time.time() - t1:.1f}s\n")

    # ── Stage 2.5: Segmentazione domande ─────────────────────────────────────
    t25 = time.time()
    print("▶ Stage 2.5 — Segmentazione domande")
    ollama_per_segm = ollama if args.backend == "ollama" else None
    domande = segmenta_domande(ocr_results, ollama_per_segm, model)
    print(f"  ✓ {len(domande)} domande da {len(immagini)} immagin{'i' if len(immagini) != 1 else 'e'}"
          f" — completato in {time.time() - t25:.1f}s\n")

    # ── Stage 3: Risposte ─────────────────────────────────────────────────────
    t2 = time.time()

    if args.backend == "claude":
        print(f"▶ Stage 3 — Risposte Claude (prompt caching + {ollama_workers} paralleli)")
        print()
        client = anthropic.Anthropic(api_key=api_key)
        system_blocks = build_system_blocks(kb)
        output_lines = risposte_parallele(client, model, system_blocks, domande, ollama_workers)

    else:  # ollama
        print(f"▶ Stage 3 — Risposte Ollama RAG (top-{args.top_k}, {ollama_workers} paralleli)")
        print()
        output_lines = risposte_ollama_rag(
            ollama, model, args.embed_modello, kb,
            domande, args.top_k, ollama_workers
        )

    print(f"\n  ✓ completato in {time.time() - t2:.1f}s\n")

    # ── Stage 4: Salva ───────────────────────────────────────────────────────
    out_path = salva_risultati(output_lines, args.materia, args.immagini, model)

    print(f"▶ Risultati salvati in: {out_path}")
    print(f"  Tempo totale: {time.time() - t0:.1f}s")
    print()


if __name__ == "__main__":
    main()
