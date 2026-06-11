# Guida: lanciare il risolutore d'esame su Windows (GPU AMD)

Questa guida permette di eseguire `esame/risolvi.py` su **Windows** con un modello LLM
**completamente in locale**, sfruttando i 16 GB di VRAM della **AMD Radeon RX 7800 XT**.
Niente API key, niente costi, niente connessione Internet durante l'uso.

**Hardware di riferimento**: 32 GB RAM · AMD Radeon RX 7800 XT 16 GB VRAM  
**Modello raccomandato**: `qwen2.5:14b` (Q4_K_M, ~9 GB VRAM — tutta la GPU sfruttata, qualità
molto superiore al default 7b)

---

## A. Software da installare

Installa nell'ordine indicato. Git è già presente sul tuo PC — salta quella voce.

### 1. Driver AMD Adrenalin (aggiornato)

La RX 7800 XT è supportata nativamente da Ollama su Windows tramite lo stack ROCm/HIP.
**Il driver deve essere recente** (Adrenalin 2024 o successivo).

- Vai su: <https://www.amd.com/it/support/download/drivers.html>
- Seleziona **Radeon RX 7800 XT** → Windows 11 → scarica e installa.
- **Riavvia il PC** dopo l'installazione.

### 2. Python 3.12

- Vai su: <https://www.python.org/downloads/windows/>
- Scarica **Python 3.12.x** (Windows installer 64-bit).
- Durante l'installazione: **spunta "Add python.exe to PATH"** (prima schermata, in basso).
- Verifica: apri un nuovo terminale (`cmd` o PowerShell) e digita:
  ```
  python --version
  ```
  Deve rispondere `Python 3.12.x`.

### 3. Git

Già installato. Verifica con:
```
git --version
```

### 4. Tesseract OCR (con lingua italiana)

Tesseract è il motore OCR che legge le immagini delle domande d'esame.

- Vai su: <https://github.com/UB-Mannheim/tesseract/wiki>
- Scarica **tesseract-ocr-w64-setup-5.x.x.exe** (versione 64-bit, la più recente).
- Durante l'installazione:
  - Nella schermata "Additional language data", scorri e **spunta "Italian"** (italiano).
  - Lascia il percorso default: `C:\Program Files\Tesseract-OCR`.
- Aggiungi Tesseract al PATH:
  1. Cerca "variabili d'ambiente" nel menu Start → "Modifica le variabili d'ambiente di sistema".
  2. Variabili di sistema → `Path` → Modifica → Nuovo.
  3. Aggiungi: `C:\Program Files\Tesseract-OCR`
  4. OK su tutte le finestre.
- Riapri il terminale e verifica:
  ```
  tesseract --version
  tesseract --list-langs
  ```
  Nella lista deve comparire `ita`.

### 5. Poppler for Windows (opzionale — serve per leggere PDF)

Poppler fornisce `pdftotext.exe` per estrarre testo dai PDF di studio.
**Non è necessario se usi solo `quizdidattica`** (il materiale è già in formato testuale),
ma è consigliato per un uso completo.

- Vai su: <https://github.com/oschwartz10612/poppler-windows/releases>
- Scarica l'ultima release (file `.zip` o `.7z`).
- Estrai in una cartella a piacere, es. `C:\poppler`.
- Aggiungi al PATH la sottocartella `Library\bin`:
  - Stessa procedura del punto 4 → aggiungi `C:\poppler\Library\bin`.
- Verifica:
  ```
  pdftotext -v
  ```

### 6. Ollama for Windows

Ollama è il server che fa girare il modello LLM in locale sulla GPU.
L'installer Windows include già lo stack GPU per AMD (ROCm/HIP) — **non serve WSL2**.

- Vai su: <https://ollama.com/download>
- Scarica e installa **Ollama for Windows**.
- Al termine Ollama si avvia automaticamente nel tray di sistema (icona nell'angolo in basso a destra).
- Verifica:
  ```
  ollama --version
  ```

---

## B. Scaricare il codice

Apri il **Prompt dei comandi** (`cmd`) e digita:

```cmd
cd %USERPROFILE%
git clone https://github.com/AndreaValenziano/andreavalenziano.github.io.git
cd andreavalenziano.github.io
```

Il codice è ora in `C:\Users\<TuoNome>\andreavalenziano.github.io`.

---

## C. Creare l'ambiente Python e installare le dipendenze

Dalla cartella `andreavalenziano.github.io` (devono essere già lì dal passaggio B):

```cmd
python -m venv esame\.venv
esame\.venv\Scripts\python.exe -m pip install --upgrade pip
esame\.venv\Scripts\python.exe -m pip install -r esame\requirements.txt
```

> Il venv viene creato in `esame\.venv` perché `avvia.bat` si aspetta il Python lì.

Verifica che tutto sia installato correttamente:
```cmd
esame\.venv\Scripts\python.exe esame\risolvi.py --help
```
Deve stampare l'elenco degli argomenti disponibili senza errori.

---

## D. Scaricare i modelli Ollama (una tantum)

Questi download richiedono spazio su disco (~9 GB per il modello chat, ~300 MB per l'embedder).
Vanno fatti una sola volta; Ollama li memorizza localmente.

```cmd
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

**Verifica che la GPU venga usata:**

1. Apri un secondo terminale.
2. Lancia il modello brevemente:
   ```cmd
   ollama run qwen2.5:14b "ciao"
   ```
3. Nel primo terminale digita:
   ```cmd
   ollama ps
   ```
4. La colonna `PROCESSOR` deve mostrare **`100% GPU`**.
   Se mostra `100% CPU` il driver o l'installer Ollama non vedono la GPU — vedi sezione F.

---

## E. Avviare il risolutore

Dalla root del repo (`andreavalenziano.github.io`), questo è il comando principale:

```cmd
esame\avvia.bat --immagini quizdidattica\screen_esame --materia quizdidattica --backend ollama --modello qwen2.5:14b --top-k 8
```

| Argomento | Significato |
|---|---|
| `--immagini quizdidattica\screen_esame` | Cartella con gli screenshot delle domande |
| `--materia quizdidattica` | Cartella con i materiali di studio |
| `--backend ollama` | Usa il modello locale (offline, gratuito) |
| `--modello qwen2.5:14b` | Modello ottimizzato per 16 GB VRAM |
| `--top-k 8` | Brani del materiale recuperati per domanda (RAG) |

Lo script stampa l'avanzamento in tempo reale:
```
▶ Stage 1 — Knowledge base        ← carica i materiali di studio
▶ Stage 2 — OCR (N immagini)      ← legge il testo dagli screenshot
▶ Stage 3 — Risposte Ollama RAG   ← il modello risponde con grounding
▶ Risultati salvati in: esame\risultati_YYYYMMDD_HHMMSS.md
```

Il file di risultati contiene il testo OCR + la risposta consigliata (lettera + confidenza)
per ogni domanda.

### Prima esecuzione (più lenta)

Al primo avvio la knowledge base viene chunked e embedduta con `nomic-embed-text`.
Il risultato è salvato in `esame\.cache\emb_*.npz` — dalla seconda volta questa fase
è istantanea (cache su disco).

---

## F. Risoluzione problemi

| Errore | Causa | Soluzione |
|---|---|---|
| `TesseractNotFoundError` | Tesseract non nel PATH | Riapri il terminale dopo aver aggiunto il PATH; riavvia il PC se necessario |
| `ita.traineddata not found` | Lingua italiana non installata | Reinstalla Tesseract selezionando "Italian" |
| `pdftotext non trovato` | Poppler non nel PATH | Installa Poppler (sezione A.5) oppure ignora se usi solo materiali `.md` |
| `Ollama non raggiungibile` | Server non avviato | Lancia `ollama serve` in un terminale separato, oppure apri l'app Ollama dal menu Start |
| Modello non trovato | Pull non completato | Riesegui `ollama pull qwen2.5:14b` |
| GPU non usata / molto lento | Driver AMD vecchio o non riconosciuto | Aggiorna al driver Adrenalin più recente e reinstalla Ollama; controlla `ollama ps` |
| `python non riconosciuto` | Python non nel PATH | Reinstalla Python con "Add python.exe to PATH" spuntato |
| `pip install` fallisce su `numpy` | Visual C++ runtime mancante | Installa [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) |
| Errore `avvia.bat` — `.venv` non trovato | Venv non creato o percorso sbagliato | Assicurati di essere nella root `andreavalenziano.github.io` quando lanci `esame\avvia.bat`, e che il venv sia stato creato con `python -m venv esame\.venv` |

---

## G. Riepilogo comandi rapidi (copia-incolla)

```cmd
REM — Una tantum (installazione) —
python -m venv esame\.venv
esame\.venv\Scripts\python.exe -m pip install --upgrade pip
esame\.venv\Scripts\python.exe -m pip install -r esame\requirements.txt
ollama pull qwen2.5:14b
ollama pull nomic-embed-text

REM — Ogni volta che usi il tool —
esame\avvia.bat --immagini quizdidattica\screen_esame --materia quizdidattica --backend ollama --modello qwen2.5:14b --top-k 8
```

---

## H. Note sul modello scelto

Il default del codice è `qwen2.5:7b` (~5 GB VRAM). Con i tuoi **16 GB di VRAM** puoi usare
`qwen2.5:14b` che:

- occupa ~9 GB in VRAM (tutto in GPU, nessuno swap in RAM),
- ha qualità di comprensione e ragionamento significativamente superiore,
- produce comunque JSON puro (necessario per il codice — `format="json"` già impostato),
- raggiunge ~30–50 tok/s sulla RX 7800 XT: veloce per uso interattivo.

Se in futuro vuoi più qualità ancora, puoi provare `qwen2.5:32b` con quantizzazione
Q3_K_M (~13 GB VRAM) oppure `qwen3:14b`. Per quest'ultimo testa l'output JSON:
la modalità "thinking" può produrre testo extra che rompe il parser — in quel caso
torna su `qwen2.5:14b`.
