# Guida — Scheda Palestra

Questa guida ti accompagna, passo per passo, nel mettere online la tua app **Scheda Palestra**.
Non serve saper programmare: basta seguire i punti nell'ordine.

Ti servono solo due cose gratuite:
- un account **Supabase** (dove vengono salvati i tuoi dati),
- un account **GitHub** (dove viene pubblicata la pagina web).

---

## 1. Creare l'account e il progetto su Supabase

1. Vai su **[supabase.com](https://supabase.com)** e premi **Start your project** / **Sign up**. Puoi registrarti con GitHub o con email.
2. Dopo l'accesso, premi **New project**.
3. Compila i campi:
   - **Name**: un nome a piacere, per esempio `scheda-palestra`.
   - **Database Password**: scegli una password per il database e **annotala** (ti servirà solo in casi particolari, non per l'app).
   - **Region**: scegli una regione **europea**, per esempio **Central EU (Frankfurt)** o **West EU (Ireland)**. Più è vicina, più l'app sarà veloce.
4. Premi **Create new project** e attendi 1–2 minuti che il progetto venga preparato.

---

## 2. Trovare e inserire le chiavi (SUPABASE_URL e SUPABASE_ANON_KEY)

1. Nel progetto Supabase, apri in basso a sinistra **Project Settings** (l'icona dell'ingranaggio) → **API**.
2. Trovi due valori che ti servono:
   - **Project URL** → è il tuo **SUPABASE_URL** (qualcosa tipo `https://abcdxyz.supabase.co`).
   - **Project API keys → anon / public** → è la tua **SUPABASE_ANON_KEY** (una stringa molto lunga). Premi **Copy** per copiarla.
   > La chiave `anon` è pensata per essere pubblica: va bene inserirla nel file. **Non** usare mai la chiave `service_role`.
3. Apri il file **`index.html`** con un editor di testo (va bene anche il Blocco note / TextEdit) e cerca, in alto nello `<script>`, queste due righe:
   ```js
   const SUPABASE_URL = '';
   const SUPABASE_ANON_KEY = '';
   ```
4. Incolla i tuoi valori **tra gli apici**, così:
   ```js
   const SUPABASE_URL = 'https://abcdxyz.supabase.co';
   const SUPABASE_ANON_KEY = 'eyJhbGciOi...la-tua-chiave-lunga...';
   ```
5. Salva il file.

---

## 3. Creare la tabella e la sicurezza dei dati

1. In Supabase, apri a sinistra **SQL Editor** e premi **New query**.
2. Incolla **esattamente** questo script:
   ```sql
   create table app_state (
     user_id uuid references auth.users primary key,
     data jsonb,
     updated_at timestamptz default now()
   );
   alter table app_state enable row level security;
   create policy "own state" on app_state
     for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
   ```
3. Premi **Run** (in basso a destra). Se compare **Success**, hai finito questo passaggio.
   > Questo crea la tabella dove finiscono i tuoi dati e attiva una regola di sicurezza: ogni utente può vedere e modificare **solo** i propri dati.

---

## 4. Creare il tuo utente per il login

1. In Supabase, apri a sinistra **Authentication** → **Users**.
2. Premi **Add user** → **Create new user**.
3. Inserisci la tua **email** e una **password** a tua scelta e conferma.
   > Questi sono i dati che userai per **accedere all'app**. Ricordateli bene.
   > (Se preferisci, spunta l'opzione per considerare l'email già confermata, così eviti passaggi di verifica.)

Con questo, la parte Supabase è completa.

---

## 5. Pubblicare l'app su GitHub Pages

1. Vai su **[github.com](https://github.com)** e accedi (o crea un account gratuito).
2. Premi **New** per creare un nuovo **repository**:
   - dai un nome, per esempio `scheda-palestra`,
   - impostalo su **Public**,
   - premi **Create repository**.
3. Carica il file **`index.html`** (quello con le chiavi già inserite):
   - nella pagina del repository premi **Add file** → **Upload files**,
   - trascina `index.html` (e, se vuoi, anche `GUIDA.md`),
   - premi **Commit changes**.
4. Attiva GitHub Pages:
   - apri **Settings** (in alto nel repository) → **Pages** (menu a sinistra),
   - alla voce **Source** scegli **Deploy from a branch**,
   - come **Branch** seleziona **main** e cartella **/ (root)**, poi premi **Save**.
5. Attendi circa un minuto e ricarica la pagina **Pages**: comparirà l'indirizzo del sito, tipo
   `https://tuonome.github.io/scheda-palestra/`.
6. Apri quell'indirizzo **sul telefono**, fai il login con l'email e la password del punto 4 e inizia a usarlo.
   > Suggerimento iPhone/Android: dal menu del browser scegli **"Aggiungi a Home"** per avere l'icona dell'app sullo schermo, come un'applicazione vera.

Dopo il primo accesso la sessione resta salvata: non dovrai rifare il login a ogni apertura.

---

## 6. In caso di problemi

**Vedo il messaggio "App non ancora configurata".**
Le chiavi non sono state inserite. Ricontrolla il **punto 2**: i valori devono stare tra gli apici e il file va **salvato** e **ricaricato** su GitHub.

**Al login dice "Email o password non corretti".**
Verifica di usare l'email e la password create al **punto 4** (Authentication → Users), non la password del database. Le maiuscole/minuscole contano.

**Il login gira all'infinito o dà un errore rosso.**
Quasi sempre è la chiave o l'URL sbagliati (punto 2), oppure hai copiato la chiave `service_role` invece di `anon`. Ricontrolla e ricarica.

**Accedo ma i dati non si salvano (in alto compare "Errore").**
La tabella o la sicurezza non sono state create bene. Rifai il **punto 3**: apri di nuovo l'SQL Editor e riesegui lo script. Se dice che la tabella esiste già, va bene — controlla che la **policy** sia presente in **Authentication → Policies**.

**Ho cambiato telefono / cancellato la cache.**
Nessun problema: i dati sono nel cloud (Supabase). Apri l'app, fai login e ritrovi tutto. In più puoi usare **"Esporta dati"** ogni tanto per tenere una copia di sicurezza sul telefono, e **"Importa dati"** per ripristinarla.

**Voglio ripristinare la scheda di partenza.**
Basta modificare i pesi a mano. Se invece hai un backup JSON esportato in precedenza, usa **"Importa dati"** dal menu **⋯**.
