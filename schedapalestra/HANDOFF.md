# Handoff — Scheda Palestra

> Nota per una **nuova** sessione di Claude Code avviata in questa cartella:
> questo file riassume il lavoro fatto in una conversazione precedente (radicata in `…/storiasociale`,
> non recuperabile da qui con `--continue`/`--resume`). Leggi questo file + `index.html` + `GUIDA.md`
> per avere il contesto e proseguire.

## 1. Cosa è stato costruito

Web app **"Scheda Palestra"** per uso personale da telefono, pubblicabile su GitHub Pages.

- **`index.html`** — app completa in un singolo file: HTML + CSS + JS inline, vanilla, nessun framework, nessun build step. Mobile-first, italiano, tema chiaro/scuro automatico.
- **`GUIDA.md`** — guida passo-passo per utente non tecnico (setup Supabase, chiavi, SQL, utente, pubblicazione GitHub Pages, troubleshooting).

Funzionalità principali:
- **Login** email/password (Supabase Auth), sessione persistente.
- **Persistenza cloud**: tabella unica `app_state` (`user_id` PK, `data` jsonb, `updated_at`); tutto lo stato in un solo oggetto JSON; **upsert con debounce 800 ms**; indicatore "Salvo…/Salvato/Errore".
- **Tab Scheda A / Scheda B / Storico**. Ogni scheda ha blocco **riscaldamento** evidenziato in alto.
- **Card esercizio**: peso in evidenza (accento arancione) con pulsanti `−`/`+` a step per-esercizio + input modificabile, nota di riferimento (posizione/tecnica), note personali libere, campi opzionali serie/ripetizioni, etichetta "per braccio" dove serve; esercizi a corpo libero senza controlli peso.
- **Salva sessione** → snapshot data+pesi nello storico; **Storico** per esercizio con elenco data → peso e barre di andamento.
- **Esporta / Importa JSON** (menu ⋯) come backup aggiuntivo.
- Metadati esercizi (nome, note riferimento, step) sempre presi dai default via `normalize()`; dal cloud si recuperano solo i valori modificabili (peso, note personali, serie/ripetizioni, storico).

## 2. Stato configurazione

- In `index.html` (righe ~320-321) `SUPABASE_URL` e `SUPABASE_ANON_KEY` sono **già compilati**.
- **Corretto un refuso**: l'URL era `…​.supabase.com` → cambiato in `…​.supabase.co` (causava `ERR_NAME_NOT_RESOLVED` al login). DNS ed endpoint `/auth/v1/health` verificati raggiungibili.
- Chiave usata: formato `sb_publishable_...` (chiave pubblica, tipo corretto — NON la `service_role`).

## 3. Da fare / verificare lato utente

- [ ] **Creare l'utente dell'app**: console Supabase → Authentication → Users → Add user → `valenzianoa@gmail.com` + password (con "Auto Confirm User"). È diverso dall'accesso GitHub alla console Supabase.
- [ ] **Eseguire lo script SQL** del punto 3 della GUIDA (crea tabella `app_state` + abilita RLS + policy "own state"), altrimenti il login riesce ma il salvataggio dà "Errore".
- [ ] **Test login end-to-end** con le credenziali dell'utente app.

## 4. Prossimi passi tecnici possibili

- **Commit** della correzione URL (`.supabase.co`) — al momento **non ancora committato**. Nuova cartella `schedapalestra/` con `index.html`, `GUIDA.md`, `HANDOFF.md` da aggiungere al repo.
- **Pubblicazione su GitHub Pages** come da GUIDA punto 5.

## 5. File in questa cartella

- `index.html` — l'app.
- `GUIDA.md` — guida utente.
- `HANDOFF.md` — questo file.
