# esame2 — Risolutore esami v2 (estrazione visiva)

Riscrittura di `esame/risolvi.py`. La v1 usava Tesseract (OCR locale) e una
segmentazione euristica del testo: i cerchietti dei radio-button diventavano
rumore (`O)`, `( )`, `'`…), i confini tra le domande si perdevano e più domande
finivano fuse in un blocco solo — per questo uscivano 14 o 24 domande invece di 30.

## Cosa cambia nella v2

| | v1 (`esame/`) | v2 (`esame2/`) |
|---|---|---|
| Estrazione domande | Tesseract + euristiche | **Visione di Claude** con output JSON strutturato |
| Screenshot sovrapposti | duplicati / domande fuse | **deduplica automatica** (vince la versione completa) |
| Conteggio domande | silenziosamente sbagliato | verificato contro `--attese` (default 30), con ⚠ avvisi |
| `paniere.json` | ignorato | opzionale con `--paniere` (solo prove: è generato da Claude, all'esame non c'è) |
| Verificabilità risposte | flag auto-dichiarato | **citazione testuale obbligatoria** dal materiale + flag `nel_materiale` |
| Dipendenze di sistema | Tesseract, poppler, Ollama | solo `pip install anthropic` (poppler solo per PDF non ancora in cache) |

## Requisiti

- Python 3.10+
- `ANTHROPIC_API_KEY` impostata nell'ambiente
- poppler (`pdftotext`) **solo** se la materia ha PDF senza `.extracted.md` in cache

## Uso

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# Pipeline completa: estrazione + risposte
./esame2/avvia.sh --immagini quizdidattica/screen_esame --materia quizdidattica

# Solo estrazione (per poi rispondere a mano in una chat Claude)
./esame2/avvia.sh --immagini quizdidattica/screen_esame --materia quizdidattica --solo-domande
```

Su Windows: `esame2\avvia.bat` con gli stessi argomenti.

### Opzioni

| Flag | Default | Descrizione |
|---|---|---|
| `--immagini` | (obbligatorio) | cartella degli screenshot |
| `--materia` | (obbligatorio) | cartella del materiale di studio |
| `--modello` | `sonnet` | modello per le risposte: `sonnet` / `haiku` / `opus` o un ID completo |
| `--modello-visione` | `haiku` | modello per l'estrazione dagli screenshot (trascrizione: conta la velocità) |
| `--attese` | `30` | numero di domande attese; se diverso, avviso in testa al file |
| `--workers` | `8` | richieste parallele per l'estrazione |
| `--batch` | `30` | domande per richiesta nelle risposte. Default = blocco unico: il rate limiter conta tutta la KB a ogni richiesta, quindi meno richieste = meno attese. Diviso in automatico se l'output trabocca |
| `--solo-domande` | — | estrae senza rispondere (flusso manuale in chat) |
| `--paniere` | — | include `paniere.json` nella KB. **Solo per le prove**: il paniere è generato da Claude, all'esame reale quelle domande non ci saranno |
| `--includi-pdf` | — | include i PDF anche se esistono riassunti `.md` (KB molto più grande) |

## Output (salvati nella cartella materia)

- `esame2_domande_<ts>.md` — domande pulite e numerate (`## D1.` + opzioni 1–4
  nell'ordine a schermo), con eventuali ⚠ avvisi in testa. È il file da allegare
  alla chat per il flusso manuale.
- `esame2_domande_<ts>.json` — le stesse domande in JSON (riusabile).
- `esame2_risposte_<ts>.md` — foglio risposte: ✅ sull'opzione corretta
  (posizione a schermo), citazione 📖 dal materiale, sezione "⚠ da verificare"
  in testa con tutte le risposte non confermate dal materiale.

## Flusso manuale (chat Claude)

Se preferisci far rispondere una chat invece dell'API:

1. lancia con `--solo-domande`
2. apri una nuova chat Claude e allega il file domande + il materiale (+ `paniere.json`)
3. incolla il prompt di **`PROMPT_CHAT.md`**

## Costi, tempi e rate limit

- I default privilegiano velocità e costo: **haiku** per la trascrizione degli
  screenshot (compito facile) e **sonnet** per le risposte. `--modello opus`
  solo se vuoi la massima qualità e accetti tempi più lunghi.
- **Il vincolo vero è il rate limit** (misurato sugli header dell'API, tier 1):
  30.000 token di **input**/min, 8.000 token di **output**/min e 50 richieste/min
  per modello. Tre dettagli misurati:
  - il limitatore stima **tutta la KB a ogni richiesta**, anche quando poi
    viene letta dalla cache (la cache abbassa il costo, non le attese);
  - una singola richiesta sopra il budget passa se il bucket è pieno: è la
    richiesta *successiva* che aspetta;
  - l'output **non** viene riservato sul `max_tokens` richiesto (conta solo
    quello effettivo), quindi un tetto generoso non costa nulla — mentre un
    tetto basso tronca l'output e costringe a dividere il blocco.

  Da qui il default `--batch 30` = **blocco unico** con `max_tokens` ampio
  (~450/domanda + margine per il thinking): la KB viene contata una volta sola
  e non ci sono attese tra blocchi (misurato: risposte in 130s contro ~270s
  con 2-3 blocchi). Con più blocchi (`--batch` più basso) i successivi leggono
  la cache (~1/10 del prezzo) ma aspettano ~2 min l'uno con una KB da ~60k
  token; gli eventuali 429 vengono gestiti aspettando il `retry-after` e
  riprovando (`⏳` nel log). Era questo il motivo per cui la
  v1 "non faceva andare la cache": 8 richieste parallele, ognuna con tutto il
  materiale, bruciavano il limite al primo giro. Per lo stesso motivo i blocchi
  **non** vengono parallelizzati: il budget al minuto è unico per modello, in
  parallelo le attese diventerebbero solo errori 429.
- I **PDF vengono saltati** se esistono riassunti `.md` (sono gli stessi
  contenuti): tiene la KB piccola, cioè dentro i limiti. `--includi-pdf` per forzarli.
- A fine corsa vengono stampati: ⏱ durata per fase e 💾 in quante richieste la
  cache è stata letta (con i token risparmiati).
- Il flusso più economico e veloce in assoluto resta `--solo-domande` + chat
  (`PROMPT_CHAT.md`): paghi solo la trascrizione con haiku (centesimi, ~30s).

## Note

- Gli screenshot vengono ordinati per **data di modifica** (l'ordine di scatto),
  non per nome: `3.51 PM` verrebbe ordinato dopo `10.51 AM` alfabeticamente.
- Una domanda tagliata dal bordo di uno screenshot viene recuperata se compare
  completa in un altro; se non compare mai completa, viene segnalata negli avvisi.
