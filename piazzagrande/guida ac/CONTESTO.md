# Wow, che tratto! 2 — contesto di lavoro

*Wow, che tratto! – 2. Sussidio realizzato dall'Azione Cattolica dei Ragazzi*, guida per
l'educatore, cammino di fede 9-11 anni (Acr), Fondazione Apostolicam Actuositatem / Ave, 2026.
Formato quasi quadrato, 132 pagine. Struttura (dall'indice, p. 132):

- Presentazione (p. 3)
- **Prima parte – Wow, che tratto!** (p. 5): il perché (7), il come (18), il metodo (23),
  il cammino dell'anno (31)
- **Seconda parte – Il cammino di fede 2026-2027** (p. 49)
  - Prima fase *L'inizio dell'Accademia* (51): Liturgia 58, Carità – Mese del Ciao 63, Catechesi – 1° tempo 68
  - Seconda fase *La presenza del Maestro* (75): Liturgia 82, Carità – Mese della Pace 88, Catechesi – 2° tempo 92
  - Terza fase *La propria impronta* (99): Liturgia 106, Catechesi – 3° tempo 110, Carità – Mese degli incontri 117
  - Quarta fase *L'offerta* (123): Liturgia 128, Carità / Tempo Estate Eccezionale 130
- Indice (p. 132)

## Sorgente
- `scansione originali/1.pdf`, `2.pdf`: scanner piano (una pagina per foglio A4) → pp. 1-23
- `3.pdf`: foto di pagine singole → pp. 23-41
- `4.pdf`, `5.pdf`, `6.pdf`: foto di doppie pagine → pp. 44-131, più l'indice (p. 132) singolo
- Mappa file → pagina stampata: `pagine_stampate.tsv` (p-006, p-024, p-041 sono duplicati)
- Pagine assenti dalle scansioni: **6, 42, 43**. p. 50 è bianca.

## Convenzioni Markdown
- Numero di pagina: `<!-- p. N -->` come commento HTML all'inizio di ogni pagina
- Parti del volume (Prima parte, Seconda parte), Presentazione e pagine di chiusura (Indice) = H1
  (la copertina NON ha H1: il titolo del volume lo aggiunge assembla.py)
- Sezioni della Prima parte (Il perché, Il come, Il metodo, Il cammino dell'anno) e fasi
  della Seconda parte ("Prima fase – L'inizio dell'Accademia", …) = H2
- Titoli di capitolo dentro una sezione ("Le finalità del cammino in Acr", "La dinamica formativa")
  e blocchi di una fase ("Liturgia", "Carità – Mese del Ciao: La strada verso il sogno",
  "Primo tempo di catechesi – Un pieno di passioni", "Verifica prima fase") = H3
- Sottotitoli e rubriche (Fine ultimo dell'Acr, Idea di fondo, Obiettivi, Unità catechistiche di
  riferimento, Attenzioni pedagogiche, Focus sul sacramento…, Tempo ordinario / di Avvento / …,
  Analisi, Confronto con il testimone, Confronto con i documenti della fede, Confronto tra i ragazzi,
  Celebrazione, Studio, Animazione, Servizio, Appunti per la festa…, Fonti e strumenti) = H4
- Seconda parte, schema fissato dal blocco D: Idea di fondo / Obiettivi / Unità catechistiche /
  Attenzioni pedagogiche = H4 direttamente sotto l'H2 della fase; in Liturgia rubrica e titolo
  uniti in un H4 ("Focus sul sacramento del battesimo – Chiamati ad annunciare il Vangelo",
  "Tempo di Avvento – Il Maestro ci indica la via"); "Nel cammino associativo" e
  "Segno – …" = H5; domeniche e giorni liturgici = paragrafi in grassetto; sommario della
  fase = lista annidata con i numeri di pagina; box "Indicazioni per la celebrazione…" = `> [!note]`
- Titoli delle attività ("Sketchare la passione", "Diverso e uguale", "Comics Lab – Un coraggio
  da… supereroi!") e sotto-rubriche (Per i ragazzi, Per gli educatori, Pista A, Unità 1…) = H5
- Descrizione in corsivo sotto le icone di tappa (Analisi, Confronto…) = paragrafo in `*corsivo*`
- Citazioni, brani biblici e box citazione = `>` blockquote, con il riferimento come nel libro
- Box "Contenuti digitali / materialiguide.azionecattolica.it" e altri riquadri informativi = `> [!note]`
- Liste di controllo delle pagine Verifica = `- [ ] domanda`
- Tabelle (es. griglia degli atteggiamenti p. 39, tabella anni liturgici p. 25) = tabella Markdown
- Schemi grafici (es. fasi temporali p. 27) = lista annidata che ne rispetti la gerarchia
- Pagine di calendario, pagine per appunti, pagine bianche e pagine di sola foto =
  una sola riga di commento, es. `<!-- p. 52: calendario settembre 2026 – gennaio 2027 -->`
- Pagine di apertura (Prima fase, Seconda parte…) = commento + titolo corrispondente
- Note a piè di pagina: `[^n]` nel testo e `[^n]: …` a fine pagina (assembla.py le rinumera per pagina)
- Corsivi dell'originale = `*…*`; grassetti = `**…**`; maiuscoletto degli autori nelle bibliografie = `**…**`
- Numeri di elenco cerchiati (① In preparazione alla festa) = H5 "1. In preparazione alla festa"

## Glossario / ortografia canonica
- **Acr** e **Ac** come nel libro (non ACR/AC); Azione Cattolica dei Ragazzi, Azione Cattolica Italiana
- Slogan dell'anno: *Wow, che tratto!*; iniziativa annuale 2026-2027: *L'Accademia del fumetto*
- Anno della sequela; icona biblica «Vino nuovo in otri nuovi» (Mc 2,18-22)
- Catechismi Cei: *cIC/2 – Venite con me* (Pista A), *cIC/3 – Sarete miei testimoni* (Pista B); scrivere `cIC/2`, `cIC/3`
- Mese del Ciao, Festa del Ciao, Mese della Pace, Mese degli incontri, Festa dell'Adesione, Tempo Estate Eccezionale
- Ic = Iniziazione cristiana; *schede-sacramento*; nelle note gli autori in maiuscoletto
  diventano **Aci**, **Ucn**, **Cei**, **Papa Francesco** (grassetto)
- *InFamiglia* (gadget-calendario), *Shemà* (percorso sulla Parola), *Bella è l'Acr*, *Sentieri di speranza*, *Work in progress*, *Guida d'arco* (pp. 44, 46) e *Guida di arco* / guide di arco (pp. 11, 24, 27): grafia come stampata
- Progetto formativo, *Perché sia formato Cristo in voi*; Cei (non CEI); Ave; materialiguide.azionecattolica.it
- Fasce d'età: 6/8, 9/11, 12/14; Piccolissimi
- Termini del fumetto in corsivo come nel libro: *sketchbook*, *comics*, *manga*, *cartoon*, *ligne claire*, *open day*, *origin story*, *uchiawase*, *workflow*, *continuity* (mangaka in tondo)
- Parola spezzata tra due pagine: resta "prota-" a fine pagina e "gonisti…" all'inizio della successiva

## Stato
- Stadio 1 (taglio): completato, 132 file in `pagine/` (`mappa_pagine.txt`, `pagine_stampate.tsv`).
  Tagli corretti a mano: `--tagli "4.pdf:5=0.53,4.pdf:11=0.478,4.pdf:12=0.478,6.pdf:7=0.512"`
- PDF da condividere: `Wow che tratto 2 - guida per l'educatore.pdf` (pp. 1-132, OCR, segnaposto per 6, 42, 43)
- Stadio 2 (OCR): Tesseract in `ocr/tesseract/`, Marker in `ocr/marker/pages/` (ocr_marker.py, 6 blocchi, ~46 min)
- Stadio 3: completato il 28 settembre 2026, 8 blocchi `md/blocco_A..H.md` → `wow_che_tratto_2.md`
  (assembla.py, ~44k parole, 38 note)
- Pagine mancanti: 6, 42, 43 (da rifotografare se servono)
- Da verificare sul libro (lettere perse al bordo della foto, integrate tra [ ] o per contesto):
  pp. 28, 32 (bordo destro), 34, 36, 40 (tre `[illeggibile]`), 65, 67, 117 (inizio righe della
  colonna sinistra: la foto è stata poi ritagliata correttamente, il testo va solo riscontrato)
- Scelte da confermare: p. 9 note 4/5 assegnate per posizione; p. 73 "uominie"/"ispirataci"
  del libro corretti in "uomini e"/"ispirata ci"; p. 88 refuso della testata "MESE DELA PACE"
  corretto; Festa/Mese degli Incontri: maiuscola come stampata nel testo, minuscola nei titoli;
  "Tempo Estivo/Estate Eccezionale" lasciati come stampati (pp. 128-129)
- Glossario aggiuntivo: Msac, *Acr Comics*, *The Catholic Cartoonist*, Festa della Pace, Pf (Progetto formativo)

## Contratto di output
Restituire SOLO Markdown. Nessun commento, nessun preambolo, nessun riassunto.
