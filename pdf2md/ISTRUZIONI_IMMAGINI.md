# Istruzioni per l'agente che descrive un lotto di immagini

Scopo: il Markdown finale è **contesto per Claude** (ripasso, domande d'esame, ricerca). Le
descrizioni devono sostituire l'immagine per chi non la vede: fedeli, dense, senza fronzoli.

Ingresso: `descrizioni/lotto_K.md` — per ogni immagine il percorso, la pagina del PDF e il testo
che la circonda nel documento. Leggi **ogni immagine** con Read (una alla volta) e usa il contesto
solo per capire di cosa si parla. Non leggere il PDF né il Markdown intero.

Uscita: scrivi `descrizioni/lotto_K.tsv` (UTF-8, una riga per immagine, nello stesso ordine,
nessuna intestazione), 4 campi separati da TAB:

```
<file>	<tipo>	<titolo>	<descrizione>
```

- `file` — il percorso esattamente come nel lotto (`img/p013-06.jpg`).
- `tipo` — `contenuto` (schema, mappa, tabella, grafico, formula, slide, foto di un esperimento o
  di uno strumento utile allo studio) oppure `decorativa` (clipart, vignetta, logo, foto
  d'atmosfera che non aggiunge informazione).
- `titolo` — 3-8 parole, diventa l'alt text (`![titolo](file)`). Obbligatorio anche per le decorative.
- `descrizione` — vuota per le decorative. Per le immagini di contenuto, **su una sola riga**
  (niente TAB né a capo; per separare le parti usa ` · `):
  - trascrivi **tutto il testo leggibile** (etichette, voci di tabella, formule: H₂O o H2O, frecce `→`);
  - rendi la struttura: mappe e diagrammi di flusso come relazioni `A → (verbo) → B`; tabelle come
    `colonna: valore; …` riga per riga; assi e andamento per i grafici; livelli per le piramidi
    (dal basso verso l'alto);
  - una frase finale su cosa mostra l'immagine rispetto al contesto, se non è ovvio;
  - **non inventare**: ciò che è illeggibile va scritto `[illeggibile]`; non aggiungere nozioni
    che non sono nell'immagine.
  - lunghezza: quanto serve, di solito 30-120 parole; tabelle e mappe grandi anche di più.

Lingua: italiano (i termini inglesi presenti nell'immagine restano in inglese).

Alla fine rispondi con una sola riga: `lotto K: N immagini (C contenuto, D decorative)`.
