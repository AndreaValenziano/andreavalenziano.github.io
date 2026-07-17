-- ============================================================================
-- Libretto — schema Supabase
-- Da eseguire nel SQL Editor del progetto https://tnslphoubwajzwxjfeti.supabase.co
-- (il database Postgres esiste già: qui si creano solo tabella, policy e RPC).
-- ============================================================================

-- ── 1. Tabella: libretto ufficiale (equivalente di voti.json) ──────────────
create table if not exists public.esami (
  id         text primary key,               -- slug stabile, es. 'letteratura-italiana'
  nome       text not null,
  anno       smallint not null default 1 check (anno between 1 and 6),
  voto       smallint not null check (voto between 18 and 30),
  lode       boolean  not null default false,
  cfu        smallint not null check (cfu between 1 and 30),
  adint      boolean  not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint lode_solo_con_30 check (not lode or voto = 30)
);

comment on table public.esami is 'Libretto ufficiale: esami registrati (fonte di verità, ex voti.json)';

-- updated_at automatico
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists trg_esami_updated_at on public.esami;
create trigger trg_esami_updated_at
  before update on public.esami
  for each row execute function public.set_updated_at();

-- ── 2. Row Level Security ───────────────────────────────────────────────────
alter table public.esami enable row level security;

-- Lettura: pubblica (la chiave publishable nel sito può solo leggere)
drop policy if exists "lettura pubblica" on public.esami;
create policy "lettura pubblica"
  on public.esami for select
  using (true);

-- Scrittura: SOLO utenti autenticati (consigliato — la pagina è pubblica su
-- GitHub Pages e la chiave publishable è visibile a chiunque).
-- Crea un utente da Dashboard → Authentication → Users → Add user,
-- poi nell'app farai login una volta sola prima di salvare.
drop policy if exists "scrittura autenticati" on public.esami;
create policy "scrittura autenticati"
  on public.esami for all
  to authenticated
  using (true)
  with check (true);

-- ALTERNATIVA (sconsigliata): scrittura aperta a chiunque abbia la chiave
-- publishable. Se preferisci partire senza login, elimina la policy sopra
-- e scommenta questa:
-- drop policy if exists "scrittura aperta" on public.esami;
-- create policy "scrittura aperta"
--   on public.esami for all
--   to anon
--   using (true)
--   with check (true);

-- ── 3. RPC: salvataggio complessivo atomico ─────────────────────────────────
-- Riceve l'intero libretto come array JSON e lo rende ufficiale:
-- upsert di tutte le righe + cancellazione di quelle non più presenti,
-- in un'unica transazione. security invoker ⇒ rispetta le RLS
-- (un anonimo può chiamarla ma delete/insert falliscono).
create or replace function public.salva_libretto(nuovi jsonb)
returns setof public.esami
language plpgsql
security invoker
set search_path = public
as $$
begin
  if jsonb_typeof(nuovi) is distinct from 'array' then
    raise exception 'salva_libretto: atteso un array JSON di esami';
  end if;
  if jsonb_array_length(nuovi) = 0 then
    raise exception 'salva_libretto: libretto vuoto, salvataggio rifiutato';
  end if;

  delete from public.esami
  where id not in (select x->>'id' from jsonb_array_elements(nuovi) x);

  insert into public.esami (id, nome, anno, voto, lode, cfu, adint)
  select
    x->>'id',
    x->>'nome',
    (x->>'anno')::smallint,
    (x->>'voto')::smallint,
    coalesce((x->>'lode')::boolean,  false),
    (x->>'cfu')::smallint,
    coalesce((x->>'adint')::boolean, false)
  from jsonb_array_elements(nuovi) x
  on conflict (id) do update set
    nome  = excluded.nome,
    anno  = excluded.anno,
    voto  = excluded.voto,
    lode  = excluded.lode,
    cfu   = excluded.cfu,
    adint = excluded.adint;

  return query select * from public.esami order by anno, nome;
end $$;

-- ── 4. Seed: contenuto attuale di voti.json (27 esami) ──────────────────────
insert into public.esami (id, nome, anno, voto, lode, cfu, adint) values
  ('adint-didattica-generale',      'AD_INT — Didattica Generale',                       1, 28, false, 2,  true ),
  ('adint-pedagogia-generale',      'AD_INT — Pedagogia Generale',                       1, 29, false, 1,  true ),
  ('adint-storia-pedagogia',        'AD_INT — Storia della Pedagogia + Educ. Comparata', 1, 28, false, 4,  true ),
  ('didattica-generale',            'Didattica Generale',                                1, 28, false, 8,  false),
  ('geografia',                     'Geografia',                                         1, 28, false, 9,  false),
  ('igiene-scolastica',             'Igiene Scolastica',                                 1, 28, false, 4,  false),
  ('letteratura-italiana',          'Letteratura Italiana',                              1, 28, false, 9,  false),
  ('metodologia-ricerca-storica',   'Metodologia della Ricerca Storica',                 1, 27, false, 8,  false),
  ('pedagogia-generale',            'Pedagogia Generale',                                1, 29, false, 8,  false),
  ('storia-pedagogia-comparata',    'Storia della Pedagogia + Educazione Comparata',     1, 26, false, 4,  false),
  ('adint-met-ric-educativa',       'AD_INT — Met. Ric. Ed. (Lab.) + Teoria e Metodi',   2, 30, false, 9,  true ),
  ('adint-educazione-ambientale',   'AD_INT — Educazione Ambientale',                    2, 30, true,  1,  true ),
  ('adint-letteratura-infanzia',    'AD_INT — Letteratura per l''Infanzia',              2, 30, false, 1,  true ),
  ('adint-psicologia-sviluppo',     'AD_INT — Psicologia dello Sviluppo',                2, 29, false, 3,  true ),
  ('educazione-ambientale',         'Educazione Ambientale',                             2, 30, true,  4,  false),
  ('letteratura-it-contemporanea',  'Letteratura Italiana Contemporanea',                2, 24, false, 4,  false),
  ('letteratura-infanzia',          'Letteratura per l''Infanzia',                       2, 30, false, 8,  false),
  ('metodologia-ricerca-educativa', 'Metodologia Ric. Educativa + Teorie e Metodi',      2, 30, false, 4,  false),
  ('pedagogia-sociale',             'Pedagogia Sociale e Interculturale',                2, 30, true,  8,  false),
  ('psicologia-sviluppo',           'Psicologia dello Sviluppo',                         2, 29, false, 5,  false),
  ('sociologia-educazione',         'Sociologia dell''Educazione',                       2, 27, false, 8,  false),
  ('ecologia',                      'Ecologia',                                          3, 28, false, 6,  false),
  ('botanica-ambientale',           'Elementi di Botanica Ambientale Applicata',         3, 25, false, 7,  false),
  ('metodologia-gioco',             'Metodologia del Gioco e dell''Animazione',          3, 30, false, 5,  false),
  ('tecnologie-didattiche',         'Tecnologie Didattiche',                             3, 30, false, 4,  false),
  ('grammatica-didattica-lingua',   'Grammatica Italiana + Didattica della Lingua',      3, 26, false, 13, false),
  ('elementi-geometria',            'Elementi di Geometria',                             3, 30, true,  6,  false)
on conflict (id) do nothing;
