# Istruzioni per la strutturazione di un blocco (Stadio 3)

Cartella di lavoro: /Users/AndreaValenziano/IdeaProjects/andreavalenziano.github.io/piazzagrande/guida ac

Stai trascrivendo in Markdown strutturato un blocco di pagine del libro
*Wow, che tratto! – 2* (guida per l'educatore Acr 9-11 anni, Azione Cattolica dei Ragazzi, 2026).
Il compito ti indica le pagine come coppie `p-NNN → p. N` (file → pagina stampata).
Per ogni file hai a disposizione:

- `ocr/marker/pages/p-NNN.md` — OCR layout-aware (Marker). È la BASE: ordine dei blocchi
  quasi sempre corretto, ma perde alcuni titoli grafici e, dove la foto è occlusa
  (rilegatura, riflessi), INVENTA parole plausibili.
- `ocr/tesseract/p-NNN.txt` — OCR Tesseract. Ordine dei blocchi spesso sbagliato, ma non
  inventa: usalo per controllare le parole dubbie.
- `pagine/p-NNN.png` — la foto della pagina. Guardala (strumento Read) per:
  (a) recuperare titoli, rubriche e intestazioni persi dall'OCR;
  (b) capire la gerarchia (titolo di capitolo, rubrica con icona, titolo di attività, box);
  (c) sciogliere i passaggi dubbi vicino alla rilegatura.
  Sui bordi delle foto di doppie pagine può comparire una striscia della pagina accanto:
  ignorala (quel testo appartiene all'altra pagina).

Leggi PRIMA `CONTESTO.md`: contiene le convenzioni Markdown obbligatorie e il glossario.
Rispettale alla lettera.

Compiti per ogni pagina:
1. Inizia la pagina con `<!-- p. N -->` (N = pagina stampata indicata nel compito).
2. Ricolloca i blocchi finiti nel posto sbagliato; ordine di lettura: colonna sinistra poi
   destra, testo principale prima dei riquadri laterali.
3. Ripristina titoli e rubriche secondo la gerarchia di CONTESTO.md (H1-H5).
4. Ricuci le parole spezzate dalla sillabazione a fine riga; un paragrafo = una riga.
5. Ripristina corsivi e grassetti dell'originale.
6. Correggi gli errori OCR evidenti; NON riscrivere, NON riassumere, NON aggiungere testo.
7. Note a piè di pagina: `[^n]` nel testo e `[^n]: …` a fine pagina (Marker le rende come `<sup>n</sup>`).
8. Pagine di sola immagine, calendario, appunti o bianche: una sola riga di commento.
   Le didascalie o le scritte nelle illustrazioni non si trascrivono.
9. Se un passaggio resta illeggibile, scrivi `[illeggibile]` senza inventare. Se al bordo della
   foto mancano poche lettere e la parola è certa dal contesto, integrale tra parentesi quadre
   (es. `comuni[tà]`); se non è certa, `[illeggibile]`.
10. Un titolo che prosegue da una pagina precedente NON va ripetuto: continua il testo.
    Se la pagina inizia a metà frase, inizia direttamente con il testo.

Output: scrivi il file `md/blocco_X.md` (X indicato nel compito) contenente SOLO il
Markdown delle pagine, in ordine di pagina stampata. Nessun preambolo, nessun commento
fuori dai commenti HTML previsti.

Rapporto finale (nella tua risposta, max 15 righe): pagine coperte, sezioni/titoli
incontrati (con la gerarchia usata), proposte per il glossario, dubbi irrisolti con
pagina, pagine rese come solo commento.
