# Prompt per rispondere alle domande in una chat Claude

## Come si usa

1. Apri una **nuova chat** su [claude.ai](https://claude.ai) (o nell'app Claude).
2. **Allega**:
   - il file delle domande estratte (`esame2_domande_*.md` oppure `esame_domande.md`)
   - il materiale di studio: i `.md` di riassunto e/o i PDF della cartella materia
   - **solo durante le prove di esercitazione**: anche `paniere.json`. Il paniere è
     stato generato da Claude — il quiz di prova attinge da lì, ma all'esame reale
     quelle domande NON ci saranno: non allegarlo all'esame vero.
3. Incolla il prompt qui sotto **così com'è** e invia.

> Consiglio: se i PDF sono molto grandi, allega prima i `.md` di riassunto.
> Se la chat segnala che gli allegati superano il limite, dividi l'esame in due chat
> (D1–D15 e D16–D30) allegando lo stesso materiale a entrambe.

---

## Prompt da incollare

```
Sei il mio assistente per un esame universitario a scelta multipla in italiano.

In allegato trovi:
1. Un file DOMANDE con domande numerate (D1, D2, …), ognuna con le opzioni
   numerate 1–4 nell'ordine in cui appaiono a schermo.
2. Il MATERIALE DI STUDIO (riassunti .md e/o PDF). Può esserci anche un
   paniere.json di esercitazione (campo "correct", indice 0-based su "opts").

Per OGNI domanda del file, nell'ordine, devi:

1. Cercare la risposta nel materiale di studio.
2. Se è allegato un paniere.json e contiene una domanda equivalente (anche
   riformulata), usa la sua risposta corretta: individua quale delle opzioni
   A SCHERMO corrisponde a quel significato. Attenzione: l'ordine delle opzioni
   a schermo può essere diverso da quello del paniere — confronta il contenuto,
   non la posizione.
3. Solo se il materiale non copre la domanda, rispondere con le tue conoscenze,
   dichiarandolo esplicitamente.

Regole vincolanti:
- NON riordinare mai le opzioni: rispondi sempre con la POSIZIONE A SCHERMO
  (1 = prima opzione dall'alto).
- Per ogni risposta cita la fonte: una breve citazione testuale del materiale,
  oppure "paniere" (se allegato), oppure "conoscenza generale".
- Confidenza "alta" solo se confermata esplicitamente dal materiale (o dal
  paniere, se allegato); altrimenti "media" o "bassa".
- Non saltare nessuna domanda. Se il file contiene N domande, voglio N risposte.
- Prima di scrivere l'output, ricontrolla le domande con confidenza non alta
  e le domande con negazioni ("quale NON…", "tranne…"): sono quelle dove si
  sbaglia più spesso.

Formato dell'output:

Prima una tabella riassuntiva:
| Domanda | Risposta | Confidenza | Fonte |

Poi, SOLO per le domande con confidenza media/bassa, un blocco di dettaglio:
### Dn — da verificare
- Risposta proposta: <numero> — <testo opzione>
- Perché: <motivazione breve>
- Alternativa plausibile: <numero, se esiste>

Chiudi con l'elenco "⚠ DA VERIFICARE: Dx, Dy, …" (vuoto se tutte ad alta confidenza).
```
