/* Wow, che tratto! 9-11 — consultazione delle attività della guida.
   I contenuti arrivano cifrati (dati.enc, generato da tools/build.py) e si
   decifrano nel browser con la password; nessuna dipendenza esterna. */
"use strict";

const AMBITI = ["Catechesi", "Carità", "Liturgia", "Estate", "Verifica"];
const K = { chiave: "wct.chiave", stato: "wct.stato", filtri: "wct.filtri", tema: "wct.tema" };
// le attività da far fare ai ragazzi stanno quasi tutte sotto Carità: lo si dice nell'etichetta
const etichetta = ambito => (ambito === "Carità" ? "Carità (attività)" : ambito);
const etichettaBlocco = b => b.replace(/^Carità(?= )/,"Carità (attività)");

const $app = document.getElementById("app");
const $nav = document.getElementById("nav");

let DATI = null;
let PER_ID = new Map();
let stato = carica(K.stato, { salvate: [], fatte: [], appunti: {}, check: {} });
let filtri = carica(K.filtri, { q: "", fasi: [], ambiti: [] });

// ---------------------------------------------------------------- memoria locale

function carica(k, def) {
  try { return Object.assign(def, JSON.parse(localStorage.getItem(k)) || {}); } catch { return def; }
}
function salva(k, v) {
  try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage non disponibile */ }
}
const salvaStato = () => salva(K.stato, stato);
const salvaFiltri = () => salva(K.filtri, filtri);
function commuta(lista, id) {
  const i = stato[lista].indexOf(id);
  i >= 0 ? stato[lista].splice(i, 1) : stato[lista].push(id);
  salvaStato();
}

// ---------------------------------------------------------------- cifratura

const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const a64 = buf => btoa(String.fromCharCode(...new Uint8Array(buf)));

async function derivaChiave(password, pacco) {
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "PBKDF2", hash: "SHA-256", salt: b64(pacco.salt), iterations: pacco.iter },
    base, { name: "AES-GCM", length: 256 }, true, ["decrypt"]);
}

async function decifra(chiave, pacco) {
  const chiaro = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(pacco.iv) }, chiave, b64(pacco.ct));
  return JSON.parse(new TextDecoder().decode(chiaro));
}

async function scaricaPacco() {
  const r = await fetch("dati.enc", { cache: "no-cache" }).catch(() => fetch("dati.enc"));
  if (!r.ok) throw new Error("Impossibile scaricare i contenuti");
  return r.json();
}

function chiaveSalvata() {
  try { return JSON.parse(localStorage.getItem(K.chiave)); } catch { return null; }
}

async function avvio() {
  let pacco;
  try { pacco = await scaricaPacco(); }
  catch { $app.innerHTML = `<div class="lucchetto"><p>Contenuti non disponibili: serve una connessione al primo avvio.</p></div>`; return; }
  const s = chiaveSalvata();
  if (s && s.salt === pacco.salt) {
    try {
      const chiave = await crypto.subtle.importKey("raw", b64(s.k), "AES-GCM", false, ["decrypt"]);
      return pronto(await decifra(chiave, pacco));
    } catch { /* chiave non più valida: si richiede la password */ }
  }
  lucchetto(pacco);
}

function lucchetto(pacco) {
  $nav.hidden = true;
  $app.innerHTML = `
    <div class="lucchetto"><form>
      <img class="logo-ac" src="img/logoac.png" alt="Azione Cattolica">
      ${logoTitolo()}
      <div class="fascia">guida per l'educatore · <b>9-11 anni</b></div>
      <p>Contenuti riservati agli educatori: inserisci la password.</p>
      <label for="pw" class="sr">Password</label>
      <input id="pw" type="password" autocomplete="current-password" required autofocus>
      <label class="ricorda"><input type="checkbox" id="ricorda" checked> Ricorda su questo dispositivo</label>
      <button class="btn primario" type="submit">Apri la guida</button>
      <p class="errore" role="alert"></p>
    </form></div>`;
  const form = $app.querySelector("form");
  collegaTema($app);
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const btn = form.querySelector("button"), err = form.querySelector(".errore");
    btn.disabled = true; btn.textContent = "Apro…"; err.textContent = "";
    try {
      const chiave = await derivaChiave(form.pw.value, pacco);
      const dati = await decifra(chiave, pacco);
      if (form.ricorda.checked) {
        salva(K.chiave, { salt: pacco.salt, k: a64(await crypto.subtle.exportKey("raw", chiave)) });
      }
      pronto(dati);
    } catch {
      err.textContent = "Password errata.";
      btn.disabled = false; btn.textContent = "Apri la guida";
      form.pw.select();
    }
  });
}

function pronto(dati) {
  DATI = dati;
  PER_ID = new Map(dati.attivita.map((a, i) => [a.id, Object.assign(a, { i, norma: norm(`${a.titolo} ${a.tappa} ${a.blocco} ${a.scopo || ""} ${a.testo}`) })]));
  $nav.hidden = false;
  window.addEventListener("hashchange", instrada);
  instrada();
}

// ---------------------------------------------------------------- utilità

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const pagine = p => (p[0] === p[1] ? `p. ${p[0]}` : `pp. ${p[0]}–${p[1]}`);
const faseDi = n => DATI.fasi.find(f => f.n === n);

function evidenzia(testo, termini) {
  let t = esc(testo);
  if (!termini.length) return t;
  const n = norm(t);
  const intervalli = [];
  for (const q of termini) {
    let i = n.indexOf(q);
    while (i >= 0) { intervalli.push([i, i + q.length]); i = n.indexOf(q, i + q.length); }
  }
  intervalli.sort((a, b) => b[0] - a[0]);
  for (const [a, b] of intervalli) t = t.slice(0, a) + "<mark>" + t.slice(a, b) + "</mark>" + t.slice(b);
  return t;
}

function estratto(a, termini) {
  if (!termini.length) return esc(a.scopo || a.testo.slice(0, 160) + "…");
  const n = norm(a.testo);
  const i = n.indexOf(termini[0]);
  if (i < 0) return esc(a.scopo || a.testo.slice(0, 160) + "…");
  const da = Math.max(0, i - 60);
  return (da ? "…" : "") + evidenzia(a.testo.slice(da, i + 140), termini) + "…";
}

// ---------------------------------------------------------------- tema e testata

function temaScuro() { return document.documentElement.dataset.theme === "dark"; }
function cambiaTema() {
  const scuro = !temaScuro();
  if (scuro) document.documentElement.dataset.theme = "dark";
  else delete document.documentElement.dataset.theme;
  try { localStorage.setItem(K.tema, scuro ? "dark" : "light"); } catch { /* ignora */ }
  document.querySelectorAll(".tema").forEach(aggiornaBottoneTema);
}
function aggiornaBottoneTema(b) {
  b.textContent = temaScuro() ? "☀" : "☾";
  b.title = b.ariaLabel = temaScuro() ? "Modalità giorno" : "Modalità notte";
}
function bottoneTema() { return `<button class="tema" type="button"></button>`; }
function collegaTema(radice = document) {
  radice.querySelectorAll(".tema").forEach(b => { aggiornaBottoneTema(b); b.addEventListener("click", cambiaTema); });
}
function logoTitolo(tag = "h1") {
  return `<${tag} class="logo-titolo"><img class="wow-img" src="img/wow.png" alt="Wow,"><span class="tratto">che tratto!</span></${tag}>`;
}
function testata() {
  return `<header class="testata">
    <div class="testata-riga">${logoTitolo()}
      <div class="strumenti"><img class="logo-ac" src="img/logoac.png" alt="Azione Cattolica">${bottoneTema()}</div>
    </div>
    <div class="fascia">guida per l'educatore · <b>9-11 anni</b> · 2026-2027</div>
  </header>`;
}

// ---------------------------------------------------------------- viste

function instrada() {
  const h = location.hash.replace(/^#\/?/, "");
  const [vista, arg] = h.split("/");
  const sezione = { "": "lista", a: "lista", fasi: "fasi", anno: "anno", salvate: "salvate" }[vista] || "lista";
  $nav.querySelectorAll("a").forEach(a => a.dataset.r === sezione ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (vista === "a" && PER_ID.has(decodeURIComponent(arg))) return vistaScheda(PER_ID.get(decodeURIComponent(arg)));
  if (vista === "fasi") return vistaFasi(arg);
  if (vista === "anno") return vistaAnno();
  if (vista === "salvate") return vistaSalvate();
  vistaLista();
}

function card(a, termini = []) {
  const salvata = stato.salvate.includes(a.id), fatta = stato.fatte.includes(a.id);
  const tag = a.tag.map(t => `<span class="tag">${esc(t)}</span>`).join(" ");
  return `<a class="card a-${a.ambito}${fatta ? " fatta" : ""}" href="#/a/${encodeURIComponent(a.id)}">
    <div class="riga1"><span class="tappa">${esc(etichetta(a.ambito))} · ${esc(a.tappa)}</span> ${tag}
      <span class="stati">${salvata ? '<span class="stella" title="Salvata">★</span>' : ""}${fatta ? '<span class="spunta" title="Fatta">✓</span>' : ""}</span></div>
    <h3>${evidenzia(a.titolo, termini)}</h3>
    <p>${estratto(a, termini)}</p>
  </a>`;
}

function elenco(lista, termini, raggruppa = true) {
  if (!lista.length) return `<div class="vuoto">Nessuna attività trovata.</div>`;
  let html = "", fase = 0, blocco = "";
  for (const a of lista) {
    if (raggruppa && a.fase !== fase) {
      fase = a.fase; blocco = "";
      const f = faseDi(fase);
      html += `<div class="gruppo-fase"><span class="num">${fase}</span><h2>${esc(f.titolo)}<small>${esc(f.etichetta)} · atteggiamento: ${esc(f.atteggiamento)}</small></h2></div>`;
    }
    if (raggruppa && a.blocco !== blocco) {
      blocco = a.blocco;
      html += `<div class="gruppo-blocco">${esc(etichettaBlocco(blocco))}</div>`;
    }
    html += card(a, termini);
  }
  return html;
}

function filtra() {
  const termini = norm(filtri.q).split(/\s+/).filter(t => t.length > 1);
  const lista = DATI.attivita.filter(a =>
    (!filtri.fasi.length || filtri.fasi.includes(a.fase)) &&
    (!filtri.ambiti.length || filtri.ambiti.includes(a.ambito)) &&
    termini.every(t => a.norma.includes(t)));
  return { lista, termini };
}

function vistaLista() {
  document.title = "Wow, che tratto! 9-11";
  const chipFase = DATI.fasi.map(f => `<button class="chip" data-fase="${f.n}" aria-pressed="${filtri.fasi.includes(f.n)}">${f.n}ª · ${esc(f.titolo)}</button>`).join("");
  const chipAmbito = AMBITI.map(a => `<button class="chip a-${a}" data-ambito="${a}" aria-pressed="${filtri.ambiti.includes(a)}"><span class="pallino" style="background:var(--c)"></span>${etichetta(a)}</button>`).join("");
  $app.innerHTML = `<div class="wrap">
    ${testata()}
    <div class="cerca">
      <input type="search" id="q" placeholder="Cerca un'attività, un materiale, un brano…" value="${esc(filtri.q)}" autocomplete="off" enterkeyhint="search">
      <div class="chips" role="group" aria-label="Filtra per ambito">${chipAmbito}</div>
      <div class="chips" role="group" aria-label="Filtra per fase">${chipFase}</div>
      <div class="conteggio"><span id="conta"></span><button id="azzera" hidden>Azzera filtri</button></div>
    </div>
    <div id="risultati"></div>
    ${piede()}
  </div>`;
  const aggiorna = () => {
    const { lista, termini } = filtra();
    document.getElementById("risultati").innerHTML = elenco(lista, termini);
    document.getElementById("conta").textContent = `${lista.length} ${lista.length === 1 ? "scheda" : "schede"}`;
    document.getElementById("azzera").hidden = !(filtri.q || filtri.fasi.length || filtri.ambiti.length);
  };
  const q = document.getElementById("q");
  q.addEventListener("input", () => { filtri.q = q.value; salvaFiltri(); aggiorna(); });
  $app.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
    const [lista, v] = c.dataset.fase ? ["fasi", +c.dataset.fase] : ["ambiti", c.dataset.ambito];
    const i = filtri[lista].indexOf(v);
    i >= 0 ? filtri[lista].splice(i, 1) : filtri[lista].push(v);
    c.setAttribute("aria-pressed", i < 0);
    salvaFiltri(); aggiorna();
  }));
  document.getElementById("azzera").addEventListener("click", () => {
    filtri = { q: "", fasi: [], ambiti: [] }; salvaFiltri(); vistaLista();
  });
  collegaPiede();
  collegaTema($app);
  aggiorna();
  ripristinaScroll();
}

function vistaScheda(a) {
  document.title = `${a.titolo} · Wow, che tratto!`;
  const f = faseDi(a.fase);
  const lista = filtra().lista;
  let pos = lista.indexOf(a);
  const vicini = pos >= 0 ? lista : DATI.attivita;
  if (pos < 0) pos = a.i;
  const prec = vicini[pos - 1], succ = vicini[pos + 1];
  const salvata = stato.salvate.includes(a.id), fatta = stato.fatte.includes(a.id);
  $app.innerHTML = `<div class="wrap a-${a.ambito}">
    <div class="barra"><a class="indietro" href="#/">← Attività</a><span class="posizione">${pos + 1} di ${vicini.length}</span></div>
    <header class="scheda-testa">
      <span class="ambito">${esc(etichetta(a.ambito))}</span>
      <div class="tappa">${esc(a.tappa)}${a.tag.length ? " · " + a.tag.map(esc).join(", ") : ""}</div>
      <h1>${esc(a.titolo)}</h1>
      <div class="meta"><a href="#/fasi/${a.fase}">${esc(f.etichetta)} – ${esc(f.titolo)}</a> · ${esc(etichettaBlocco(a.blocco))} · ${pagine(a.pagine)} della guida</div>
    </header>
    ${a.scopo ? `<div class="fumetto"><b>Obiettivo</b>${esc(a.scopo)}</div>` : ""}
    <div class="azioni">
      <button class="btn" id="salva" aria-pressed="${salvata}">★ ${salvata ? "Salvata" : "Salva"}</button>
      <button class="btn" id="fatta" aria-pressed="${fatta}">✓ ${fatta ? "Fatta" : "Segna come fatta"}</button>
      ${navigator.share ? '<button class="btn" id="condividi">Condividi link</button>' : ""}
    </div>
    <article class="contenuto">${a.html}</article>
    <div class="appunti">
      <label for="appunti">I miei appunti</label>
      <textarea id="appunti" placeholder="Adattamenti, materiali da preparare, com'è andata…">${esc(stato.appunti[a.id] || "")}</textarea>
      <small>Salvati solo su questo dispositivo.</small>
    </div>
    <nav class="naviga">
      ${prec ? `<a class="prec" href="#/a/${encodeURIComponent(prec.id)}"><small>← Precedente</small>${esc(prec.titolo)}</a>` : ""}
      ${succ ? `<a class="succ" href="#/a/${encodeURIComponent(succ.id)}"><small>Successiva →</small>${esc(succ.titolo)}</a>` : ""}
    </nav>
  </div>`;
  window.scrollTo(0, 0);

  const bottone = (id, lista, si, no) => {
    const b = document.getElementById(id);
    b.addEventListener("click", () => {
      commuta(lista, a.id);
      const on = stato[lista].includes(a.id);
      b.setAttribute("aria-pressed", on);
      b.textContent = b.textContent[0] + " " + (on ? si : no);
    });
  };
  bottone("salva", "salvate", "Salvata", "Salva");
  bottone("fatta", "fatte", "Fatta", "Segna come fatta");
  document.getElementById("condividi")?.addEventListener("click", () =>
    navigator.share({ title: a.titolo, url: location.href }).catch(() => {}));
  const ta = document.getElementById("appunti");
  ta.addEventListener("input", () => {
    ta.value.trim() ? (stato.appunti[a.id] = ta.value) : delete stato.appunti[a.id];
    salvaStato();
  });
  // le liste di controllo (Verifica) ricordano le spunte
  const box = [...$app.querySelectorAll(".contenuto input[type=checkbox]")];
  const segnate = stato.check[a.id] || [];
  box.forEach((c, i) => {
    c.checked = segnate.includes(i);
    c.addEventListener("change", () => {
      stato.check[a.id] = box.flatMap((x, j) => (x.checked ? [j] : []));
      if (!stato.check[a.id].length) delete stato.check[a.id];
      salvaStato();
    });
  });
}

function vistaFasi(apri) {
  document.title = "Le fasi · Wow, che tratto!";
  const conta = n => DATI.attivita.filter(a => a.fase === n && a.ambito !== "Verifica").length;
  $app.innerHTML = `<div class="wrap">
    <h1 class="titolo-pagina">Le quattro fasi</h1>
    ${DATI.fasi.map(f => `<section class="fase" id="fase-${f.n}">
      <div class="fase-testa"><span class="num">${f.n}</span><div><h2>${esc(f.titolo)}</h2><small>${esc(f.etichetta)} · ${pagine(f.pagine)}</small></div></div>
      <div class="atteggiamento">Atteggiamento prevalente <strong>${esc(f.atteggiamento)}</strong></div>
      <ul class="obiettivi">${f.obiettivi.map(o => `<li>${o}</li>`).join("")}</ul>
      ${f.sezioni.filter(s => s.titolo !== "Obiettivi").map(s => `<details class="sez"><summary>${esc(s.titolo)}</summary><div class="contenuto">${s.html}</div></details>`).join("")}
      <button class="btn vai" data-fase="${f.n}">Vedi le ${conta(f.n)} attività →</button>
    </section>`).join("")}
  </div>`;
  $app.querySelectorAll(".vai").forEach(b => b.addEventListener("click", () => {
    filtri = { q: "", fasi: [+b.dataset.fase], ambiti: [] }; salvaFiltri(); location.hash = "#/";
  }));
  if (apri) document.getElementById(`fase-${apri}`)?.scrollIntoView();
  else window.scrollTo(0, 0);
}

function vistaAnno() {
  document.title = "L'anno · Wow, che tratto!";
  $app.innerHTML = `<div class="wrap anno">
    <h1 class="titolo-pagina">Il cammino dell'anno</h1>
    <p>L'essenziale della prima parte della guida: domanda di vita, brano biblico, atteggiamenti e iniziativa annuale.</p>
    <div class="fase">${DATI.anno.map((s, i) => `<details class="sez"${i === 1 ? " open" : ""}><summary>${esc(s.titolo)}</summary><div class="contenuto">${s.html}<p class="meta"><small>${pagine(s.pagine)} della guida</small></p></div></details>`).join("")}</div>
  </div>`;
  window.scrollTo(0, 0);
}

function vistaSalvate() {
  document.title = "Salvate · Wow, che tratto!";
  const salvate = DATI.attivita.filter(a => stato.salvate.includes(a.id));
  const conAppunti = DATI.attivita.filter(a => stato.appunti[a.id] && !stato.salvate.includes(a.id));
  const tot = DATI.attivita.filter(a => a.ambito !== "Verifica");
  const fatte = tot.filter(a => stato.fatte.includes(a.id)).length;
  $app.innerHTML = `<div class="wrap">
    <h1 class="titolo-pagina">Le mie attività</h1>
    <p class="conteggio">Aspetto: ${bottoneTema()}</p>
    <p class="conteggio">Svolte con il gruppo: ${fatte} su ${tot.length}</p>
    <div class="gruppo-blocco">★ Salvate</div>
    ${salvate.length ? elenco(salvate, [], false) : `<div class="vuoto">Tocca ★ Salva in una scheda per ritrovarla qui.</div>`}
    ${conAppunti.length ? `<div class="gruppo-blocco">Con appunti</div>${elenco(conAppunti, [], false)}` : ""}
  </div>`;
  collegaTema($app);
  window.scrollTo(0, 0);
}

function piede() {
  return `<footer class="piede">
    <span>Contenuti © Fondazione Apostolicam Actuositatem – Ave 2026. Uso riservato agli educatori.</span>
    <button id="esci">Dimentica la password</button>
  </footer>`;
}
function collegaPiede() {
  document.getElementById("esci")?.addEventListener("click", () => {
    try { localStorage.removeItem(K.chiave); } catch { /* ignora */ }
    location.hash = ""; location.reload();
  });
}

// ricorda la posizione nella lista quando si torna da una scheda
let scrollLista = 0;
window.addEventListener("scroll", () => { if (!location.hash.startsWith("#/a/") && /^#?\/?$/.test(location.hash)) scrollLista = window.scrollY; }, { passive: true });
function ripristinaScroll() { requestAnimationFrame(() => window.scrollTo(0, scrollLista)); }

if ("serviceWorker" in navigator && location.protocol !== "file:") {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
avvio();
