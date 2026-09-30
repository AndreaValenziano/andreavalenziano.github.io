# Istruzioni per la strutturazione di un blocco (Stadio 3)

Cartella di lavoro: /Users/AndreaValenziano/IdeaProjects/andreavalenziano.github.io/guideac/piazza grande

Stai trascrivendo in Markdown strutturato un blocco di pagine del libro
*piazza grande 2026|2027* (guida educatori giovani, Azione Cattolica Italiana, Ave 2026).
Per ogni pagina p-NNN del tuo intervallo hai a disposizione:

- `ocr/marker/pages/p-NNN.md` — OCR layout-aware (Marker). È la BASE: ordine dei blocchi
  quasi sempre corretto, ma perde alcuni titoli grafici, i numeri di pagina, e dove la
  foto è occlusa (vicino alla rilegatura) INVENTA parole plausibili.
- `ocr/tesseract/p-NNN.txt` — OCR Tesseract. Ordine dei blocchi sbagliato, ma non inventa:
  usalo per controllare le parole dubbie.
- `pagine/p-NNN.png` — la foto della pagina. Guardala (strumento Read) SOLO per:
  (a) recuperare titoli di sezione, rubriche e numeri di pagina persi dall'OCR;
  (b) capire a quale tipo di riquadro appartiene un testo (post-it, box tondo, citazione PF…);
  (c) sciogliere i passaggi dubbi vicino alla rilegatura.
  Non trascrivere dall'immagine ciò che l'OCR ha già reso bene.

Leggi PRIMA `CONTESTO.md`: contiene le convenzioni Markdown obbligatorie e il glossario
con la grafia canonica. Rispettale alla lettera.

Compiti per ogni pagina:
1. Inizia la pagina con `<!-- p. N -->` dove N è il numero di pagina STAMPATO nel libro
   (in basso). Se non è leggibile, deducilo dalle pagine vicine e scrivi `<!-- p. N? -->`.
2. Ricolloca i blocchi finiti nel posto sbagliato; il testo principale prima dei riquadri.
3. Ripristina titoli e rubriche (gerarchia: modulo H1, sezione/sottomodulo H2, rubrica H3).
4. Ricuci le parole spezzate dalla sillabazione a fine riga; un paragrafo = una riga.
5. Ripristina i corsivi dell'originale (titoli di opere, parole straniere, citazioni in corsivo).
6. Correggi gli errori OCR evidenti; NON riscrivere, NON riassumere, NON aggiungere testo.
7. Note a piè di pagina: `[^n]` nel testo e definizione `[^n]: …` a fine pagina.
8. Pagine di sola immagine, apertura di modulo o pubblicità: una sola riga di commento,
   es. `<!-- p. 40: pagina fotografica di apertura del sottomodulo "Dono" -->` oppure
   `<!-- p. 114-115: pubblicità Parole di Giustizia e Speranza -->`. Non trascrivere le
   pubblicità.
9. Se un passaggio resta illeggibile, scrivi `[illeggibile]` senza inventare.

Output: scrivi il file `md/blocco_X.md` (X indicato nel compito) contenente SOLO il
Markdown delle pagine nell'ordine dei file p-NNN (cioè l'ordine delle foto, anche se
non coincide con quello del libro). Nessun preambolo, nessun commento fuori dai
commenti HTML previsti.

Rapporto finale (nella tua risposta, max 15 righe): intervallo di pagine stampate
coperto (es. "pp. 14-27"), moduli/sezioni incontrati, proposte per il glossario
(nomi, sigle, grafie ricorrenti), dubbi irrisolti con pagina, pagine saltate perché
immagine/pubblicità.
