# Digitalizzazione "piazza grande 2026|2027" — Runbook

Conversione di un libro fotografato in PDF verso un file Markdown strutturato.
Questo documento è pensato per essere passato a un agente (Claude Code) come
briefing operativo completo. Contiene la diagnostica già fatta, la pipeline,
i comandi e le convenzioni di output.

---

## 1. Il materiale

| Proprietà | Valore |
|---|---|
| Sorgente | Fotografie da iPhone/Mac, esportate con Anteprima (macOS) |
| Layer di testo | **Assente** (`pdffonts` restituisce tabella vuota) → OCR obbligatorio |
| Pagine PDF | **68**: 54 doppie pagine (orizzontali) + 14 pagine singole (verticali) |
| Pagine libro attese | **~120** (54 × 2 + 14 = 122) |
| Formato pagina PDF | Variabile, 1 pt = 1 px della foto (es. doppia ~1850 × 1350 pt) → risoluzione nativa 72 DPI |
| Peso | ~3,7 MB/pagina → 254 MB |

### Caratteristiche da tenere presenti

1. **Le doppie pagine sono già dritte** (orientamento orizzontale, nessuna
   rotazione nel PDF attuale). Usare `--rot 0`. *(Una versione precedente
   dell'export le aveva ruotate di 90°: se ricompare, `--rot 90` = antiorario.)*

2. **Le pagine singole sono 14, non solo copertina e retro**: 1, 2, 14, 19,
   21, 22, 27, 28, 32, 35, 42, 43, 44, 53. Sono tutte verticali e già dritte:
   `split_libro.py --skip auto` le riconosce dall'orientamento (altezza >
   larghezza) e non le taglia.

3. **Risoluzione effettiva bassa.** La doppia pagina è ~1650-1850 × 1226-1350
   px, quindi ogni pagina del libro ha ~825-925 px di larghezza, cioè
   **110-150 DPI effettivi** contro i 300 che Tesseract preferirebbe. Il peso
   del file deriva dalla compressione JPEG blanda, non dal dettaglio. Le pagine
   PDF sono dimensionate 1 pt = 1 px, quindi **il rendering nativo è a 72 DPI**:
   `--dpi 144` raddoppia (utile a Tesseract), oltre non si guadagna nulla.

4. **È una fotografia, non una scansione piana.** Presenti: ombre verso la
   rilegatura, curvatura delle pagine, leggera prospettiva, margini irregolari.

5. **Layout da rivista, non da libro.** Riquadri colorati, post-it gialli,
   box tondi con domande, frecce decorative, firme in corsivo manoscritto,
   titoli in font display, numeri di pagina laterali. **Questo è il vero
   problema del progetto, non l'OCR.**

### Risultati del test OCR (già eseguito)

- **Pagine di sola prosa**: Tesseract `-l ita --psm 3` produce risultato
  quasi perfetto. ~2-3 errori su 350 parole. Apostrofi e sillabazione a fine
  riga conservati correttamente.
- **Pagine impaginate**: il testo viene estratto tutto, ma **l'ordine di
  lettura è sbagliato**. Il contenuto dei riquadri laterali si infila dentro
  i paragrafi del testo principale, spezzato su più righe. I titoli di sezione
  con elementi grafici vengono persi del tutto.

**Conclusione**: Tesseract è sufficiente per la prosa, insufficiente per le
pagine strutturate. Serve uno strumento layout-aware per queste ultime.

---

## 2. Stadio 1 — Normalizzazione geometrica

Lo script `split_libro.py` (allegato) rende il PDF in immagini, ruota, taglia
le doppie pagine in singole, salta le pagine già singole e ricompone un PDF.

```bash
python3 split_libro.py "PIAZZA GRANDE.pdf" singole.pdf --skip auto --rot 0 --dpi 144
```

Parametri:

- `--skip` — elenco separato da virgole delle pagine già singole (1-based),
  oppure `auto`: sono singole le pagine con altezza > larghezza (dopo la
  rotazione, se richiesta).
- `--dpi` — DPI di rendering. 144 è il valore giusto per questo PDF (2× il
  nativo); oltre non si guadagna nulla perché la sorgente non ha quel dettaglio.
- `--rot` — `0` per il PDF attuale (doppie già orizzontali); `90` antiorario,
  `-90` orario se le doppie risultano ruotate.
- `--offset` — sposta la linea di taglio in percentuale della larghezza
  (da -20 a 20). Serve quando la rilegatura non cade esattamente a metà.

**Verifica obbligatoria prima di procedere**: controllare 4-5 pagine sparse
(inizio, metà, fine) e confermare che il taglio cada sulla rilegatura e che
nessuna riga di testo venga amputata ai bordi. Se il taglio è disallineato in
modo diverso tra inizio e fine del libro, processare il volume in due o tre
blocchi con `--offset` diversi.

### Opzionale ma consigliato: ScanTailor Advanced

Se dopo il taglio le pagine risultano storte o con forte curvatura verso la
rilegatura, passare `singole.pdf` attraverso **ScanTailor Advanced** prima
dell'OCR: deskew, dewarp, normalizzazione dell'illuminazione, ritaglio del
contenuto. È nato per digitalizzare libri e migliora sensibilmente la resa OCR
su fotografie. Alternativa più rapida e grossolana: **Briss**.

---

## 3. Stadio 2 — OCR e conversione in Markdown

**Eseguire entrambe le opzioni su un campione di 10 pagine miste** (prosa +
pagine a riquadri) e confrontare prima di lanciare sull'intero volume.

### Opzione A — Marker (layout-aware, consigliata)

```bash
# venv: Python 3.13 di Homebrew (con 3.14 torch non è disponibile); ensurepip è rotto,
# quindi il venv va creato senza pip e pip va iniettato dall'esterno. Serve inoltre il
# workaround libexpat (DYLD_LIBRARY_PATH) come in esame/avvia.sh e llama.cpp per Surya.
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib
/opt/homebrew/bin/python3.13 -m venv --without-pip .venv
/opt/homebrew/bin/pip3.13 --python .venv/bin/python install pip
.venv/bin/python -m pip install marker-pdf
brew install llama.cpp
.venv/bin/marker_single singole.pdf --output_dir ocr/marker --output_format markdown \
    --disable_image_extraction --paginate_output
```

Note sulla versione installata (settembre 2026): non esiste più `--languages`
(Surya è multilingue); l'OCR di Surya è un modello linguistico servito da
`llama-server`, quindi **dove l'immagine è occlusa inventa parole plausibili**
(es. "popolarizzano" per "popolano"): in Stadio 3 i passaggi vicini alla
rilegatura vanno confrontati con Tesseract e con l'immagine. `--paginate_output`
inserisce un separatore per pagina, indispensabile per i commenti `<!-- p. N -->`.
Tempi su Mac Apple Silicon: ~20-25 s/pagina.

Con GPU e API key disponibili, aggiungere `--use_llm`: fa una differenza
sostanziale sulle pagine a riquadri. Senza GPU, calcolare qualche minuto per
pagina.

Alternative equivalenti da valutare se Marker delude: **MinerU** (migliore su
tabelle e formule), **Docling** (licenza MIT, ottimo su CPU, output strutturato),
**pdf-craft** (specializzato su libri scansionati, interamente offline).

Nota sulla licenza: Marker è GPL-3.0 + RAIL-M sui pesi, con restrizioni
commerciali sopra una soglia di fatturato. Irrilevante per uso interno.

### Opzione B — Tesseract (baseline veloce)

```bash
ocrmypdf -l ita --force-ocr --deskew --clean singole.pdf ocr.pdf
pip install pymupdf4llm
python3 -c "import pymupdf4llm; open('grezzo.md','w').write(pymupdf4llm.to_markdown('ocr.pdf'))"
```

Gira in pochi minuti su tutto il volume. Da usare come fallback e come
riferimento di confronto.

### Criterio di scelta

Confrontare l'output delle due opzioni sulle pagine a riquadri. Vince quella
che sbaglia meno **l'ordine dei blocchi**, non quella che sbaglia meno
caratteri: gli errori di carattere si correggono in automatico, l'ordine no.

**Esito del confronto (campione di 10 pagine, 11 settembre 2026): vince Marker.**
Sulla pagina con post-it e box tondo Marker restituisce testo principale →
citazione PF → domanda → firma nell'ordine giusto, mentre Tesseract mescola i
riquadri nel corpo. Marker ricostruisce anche il testo schiacciato verso la
rilegatura (pagine destre delle doppie), che Tesseract rende illeggibile nelle
prime 2-3 lettere di ogni riga. Marker però perde alcuni titoli grafici
("Laboratori", "e per approfondire", "introduzione") e i numeri di pagina.
Output: `ocr/marker/singole/singole.md` (Marker) e `ocr/tesseract/p-NNN.txt`
(Tesseract, riferimento per il controllo delle allucinazioni).

---

## 4. Stadio 3 — Strutturazione del Markdown

Questa fase va fatta a blocchi di **10-15 pagine di libro alla volta**, su
**testo** (mai reinviare le immagini: costano 10-20 volte di più e non
aggiungono nulla a questo punto).

Compiti per ogni blocco:

1. Estrarre i blocchi di testo finiti nel posto sbagliato e ricollocarli.
2. Ripristinare i titoli di sezione persi dall'OCR (vanno riletti dal PDF
   originale se necessario).
3. Ricucire le parole spezzate dalla sillabazione a fine riga.
4. Ripristinare i corsivi, che l'OCR perde sistematicamente.
5. Normalizzare la gerarchia dei titoli.
6. Aggiornare il file di stato (vedi §5).

---

### Esito (12 settembre 2026)

Eseguito con 8 agenti in parallelo (un blocco di ~15 foto ciascuno, brief in
`md/ISTRUZIONI_BLOCCO.md`), partendo dal testo Marker e usando Tesseract come
controllo e la foto solo per titoli persi, attribuzione dei riquadri e passaggi
vicino alla rilegatura. Le foto non seguono l'ordine del libro: `assembla.py`
ricompone `md/blocco_*.md` in `piazza_grande_2026-2027.md` secondo i numeri di
pagina stampati e rinumera le note per pagina. Pagine assenti dalle foto: 24, 34,
61, 94, 96, 104, 111.

## 5. Mantenere la coerenza tra sessioni diverse

Il problema centrale del lavoro a blocchi è che ogni sessione riparte senza
memoria della precedente. La soluzione è **separare lo stato dal contenuto**:
un unico file breve, `CONTESTO.md`, che viene passato all'inizio di ogni
sessione e aggiornato alla fine.

```markdown
# piazza grande 2026|2027 — contesto di lavoro

## Convenzioni Markdown
- Titoli sezione (es. "CHI EDUCA… È UN DISCEPOLO MISSIONARIO") = H2
- Citazioni dal Progetto formativo (box colorati) = > blockquote + (PF, p. N)
- Post-it gialli con domande = > [!question]
- Box tondi arancioni ("Cosa vuol dire…?") = > [!tip]
- Firme a fine sezione = *— Nome Cognome*, ruolo
- Note a piè di pagina = [^n], raccolte a fine capitolo
- Numeri di pagina del libro = <!-- p. N --> come commento HTML
- Corsivi dell'originale = *asterischi*; maiuscoletto = **grassetto**

## Glossario / ortografia canonica
(nomi propri, sigle e termini ricorrenti, con la grafia decisa una volta
per tutte: AC, Settore giovani, Équipe, Progetto formativo, ecc.)

## Stato
- Ultimo blocco completato: pp. —
- Ultime 3 righe trascritte: "…"
- In sospeso: —

## Contratto di output
Restituire SOLO Markdown. Nessun commento, nessun preambolo, nessun riassunto.
```

Il glossario è la parte che conta di più: è ciò che impedisce che lo stesso
nome venga scritto in tre modi diversi in tre capitoli diversi.

Il commento `<!-- p. N -->` è ciò che permette di ritrovare il punto esatto
nel PDF originale quando un passaggio risulta dubbio. Vale la pena inserirlo
sistematicamente.

---

## 6. Decisione da prendere prima di iniziare

**Come rappresentare i riquadri.** Cambia poco durante la lavorazione, ma è
scomodo da modificare dopo su 120 pagine.

- Se il Markdown serve per una knowledge base o per ricerca full-text →
  callout `> [!question]`, `> [!tip]`.
- Se si prevede di rigenerare un PDF impaginato o una pagina web →
  container `:::box` … `:::`, stilizzabili a valle.

---

## 7. Alternativa da considerare seriamente

Rifotografare il libro: **pagina singola anziché doppia, dritta, luce diffusa,
300 DPI reali**. Elimina in un colpo solo la rotazione, il taglio, la curvatura,
le ombre e il deficit di risoluzione. Circa 30-40 minuti di lavoro che ne
risparmiano diverse ore di correzione a valle.

Se il volume deve essere digitalizzato bene e conservato, è la strada migliore.
Se serve una conversione "buona abbastanza" in tempi brevi, la pipeline sopra
è adeguata.

---

## 8. Nota

Il volume è un'opera pubblicata e protetta da copyright (Azione Cattolica
Italiana, Ave, 2026). La digitalizzazione per uso personale e di servizio
è una cosa; la redistribuzione del Markdown risultante è un'altra.

---

## Allegati

- `split_libro.py` — script dello Stadio 1, già testato su un campione di
  12 pagine (output: 22 pagine singole corrette).
