import type { Place, Trip } from '../types'

/**
 * Unica fonte di verità dei contenuti dell'app.
 * Generato da viaggiocascia/itinerario-umbria-2026.md: per modificare orari,
 * luoghi o note basta cambiare questo file, senza toccare i componenti.
 * Telefoni e coordinate provengono solo dai dati verificati: i campi mancanti
 * restano undefined e la UI nasconde i relativi pulsanti.
 */

const places: Place[] = [
  {
    id: 'hotel-delle-rose',
    name: 'Hotel Delle Rose',
    category: 'hotel',
    address: 'Via Madre Teresa Fasce 2, Cascia (PG)',
    mapQuery: 'Hotel Delle Rose, Via Madre Teresa Fasce 2, Cascia',
    notes:
      'Base per tutte e 3 le notti, a ~20 metri dalla Basilica di Santa Rita. Parcheggio gratuito in loco (nessun problema di ZTL a Cascia). Mezza pensione: colazione e cena incluse; l’11 la cena viene spostata a pranzo (da confermare con l’hotel).',
  },

  /* Ristoranti */
  {
    id: 'trattoria-appennino',
    name: 'Trattoria l’Appennino',
    category: 'restaurant',
    address: 'Piazzale Dante Alighieri 6, Cascia',
    phone: '+393888055527',
    phoneDisplay: '+39 388 805 5527',
    lat: 42.7156409,
    lng: 13.0139963,
    rating: 4.8,
    when: 'Pranzo · domenica 9 · Cascia',
    notes:
      'Cucina casalinga, prodotti locali: trota pescata dal titolare, agnello, cannelloni, dolci della mamma. Aperta la domenica a pranzo.',
  },
  {
    id: 'grottino-orlando',
    name: 'Trattoria Il Grottino da Orlando',
    category: 'restaurant',
    address: 'Via Roma 18, Cascia',
    phone: '+393347047014',
    phoneDisplay: '+39 334 704 7014',
    lat: 42.7176852,
    lng: 13.0134291,
    rating: 4.4,
    when: 'Pranzo · domenica 9 · Cascia',
    alternative: true,
  },
  {
    id: 'trattoria-pallotta',
    name: 'Trattoria Pallotta',
    category: 'restaurant',
    mapQuery: 'Trattoria Pallotta, Assisi',
    priceRange: 'Menù fissi €30 / €40',
    when: 'Pranzo · lunedì 10 · Assisi',
    notes: 'Cucina umbra DOC, vicino a Piazza del Comune.',
  },
  {
    id: 'ristorante-san-francesco',
    name: 'Ristorante San Francesco',
    category: 'restaurant',
    mapQuery: 'Ristorante San Francesco, Assisi',
    when: 'Pranzo · lunedì 10 · Assisi',
    notes: 'Di fronte alla Basilica, con vista sulla valle.',
  },
  {
    id: 'locanda-del-cardinale',
    name: 'La Locanda del Cardinale',
    category: 'restaurant',
    mapQuery: 'La Locanda del Cardinale, Assisi',
    when: 'Pranzo · lunedì 10 · Assisi',
    notes: 'Elegante, in un palazzo medievale con domus romana: per un pranzo più speciale.',
  },
  {
    id: 'locanda-cacio-re',
    name: 'Locanda Cacio Re',
    category: 'restaurant',
    address: 'Loc. I Casali, Vallo di Nera',
    phone: '+390743617003',
    phoneDisplay: '+39 0743 617003',
    mapQuery: 'Locanda Cacio Re, Vallo di Nera',
    priceRange: '~€40–60 a persona',
    when: 'Cena · martedì 11 · anniversario',
    notes:
      'Casale del ’500 con terrazza panoramica sulla valle del Nera. Strangozzi “Cacio Re”, tartufo nero, salumi di Norcia, trota. Prenotare il tavolo in terrazza.',
  },
  {
    id: 'taverna-del-bordone',
    name: 'La Taverna del Bordone',
    category: 'restaurant',
    mapQuery: 'La Taverna del Bordone, Vallo di Nera',
    when: 'Cena · martedì 11 · anniversario',
    alternative: true,
    notes: 'Alternativa nello stesso borgo.',
  },
  {
    id: 'ristorante-vespasia',
    name: 'Ristorante Vespasia',
    category: 'restaurant',
    mapQuery: 'Ristorante Vespasia, Norcia',
    when: 'Cena · martedì 11 · anniversario',
    alternative: true,
    notes: 'Alternativa gourmet (stella Michelin) a Norcia: menù degustazione da prenotare 24h prima.',
  },
  {
    id: 'osteria-la-cascata',
    name: 'Osteria La Cascata',
    category: 'restaurant',
    address: 'Via SS Valnerina 46, Terni',
    phone: '+390744080993',
    phoneDisplay: '+39 0744 080993',
    lat: 42.555188,
    lng: 12.7095499,
    rating: 4.5,
    when: 'Pranzo · mercoledì 12 · Marmore',
    notes: 'A due passi dalle cascate, ottima per il pranzo dopo la visita. Aperta il mercoledì a pranzo.',
  },
  {
    id: 'pavone-doro',
    name: 'Il Pavone d’Oro',
    category: 'restaurant',
    phone: '+39074462148',
    phoneDisplay: '+39 0744 62148',
    lat: 42.5562565,
    lng: 12.7176435,
    rating: 4.3,
    when: 'Pranzo · mercoledì 12 · Marmore',
    alternative: true,
    notes: 'Con vista sulla cascata.',
  },

  /* Luoghi da visitare */
  {
    id: 'basilica-santa-rita',
    name: 'Basilica di Santa Rita',
    category: 'sight',
    mapQuery: 'Basilica di Santa Rita, Cascia',
  },
  {
    id: 'roccaporena',
    name: 'Roccaporena',
    category: 'sight',
    mapQuery: 'Roccaporena, Cascia',
  },
  {
    id: 'santa-maria-degli-angeli',
    name: 'Basilica di Santa Maria degli Angeli',
    category: 'sight',
    mapQuery: 'Basilica di Santa Maria degli Angeli, Assisi',
  },
  {
    id: 'basilica-san-francesco',
    name: 'Basilica di San Francesco',
    category: 'sight',
    mapQuery: 'Basilica di San Francesco, Assisi',
  },
  {
    id: 'norcia',
    name: 'Norcia',
    category: 'sight',
    mapQuery: 'Piazza San Benedetto, Norcia',
  },
  {
    id: 'cascate-marmore',
    name: 'Cascate delle Marmore',
    category: 'sight',
    mapQuery: 'Cascate delle Marmore, Belvedere Superiore',
  },

  /* Parcheggi di Assisi */
  {
    id: 'parcheggio-saba',
    name: 'Parcheggio Saba Giovanni Paolo II',
    category: 'parking',
    mapQuery: 'Parcheggio Saba Giovanni Paolo II, Assisi',
    notes: 'Coperto, il più vicino a San Francesco. A pagamento.',
  },
  {
    id: 'parcheggio-mojano',
    name: 'Parcheggio Mojano',
    category: 'parking',
    mapQuery: 'Parcheggio Mojano, Assisi',
    notes: 'Con scale mobili verso il centro. A pagamento.',
  },
]

export const trip: Trip = {
  title: 'Umbria 2026 — Assisi, Cascia e la Valnerina',
  subtitle: 'Anniversario · 9–12 agosto 2026 · in auto da Trani',
  startDate: '2026-08-09',
  endDate: '2026-08-12',
  timezone: 'Europe/Rome',
  accommodationId: 'hotel-delle-rose',
  overview: {
    facts: [
      { label: 'Quando', value: 'Domenica 9 → mercoledì 12 agosto 2026 (3 notti)' },
      { label: 'Come', value: 'In auto, partenza da Trani' },
      { label: 'Base unica', value: 'Hotel Delle Rose, Cascia — mezza pensione, parcheggio gratuito' },
      { label: 'Anniversario', value: 'Martedì 11 agosto — cena fuori alla Locanda Cacio Re' },
      { label: 'Ritmo', value: 'Rilassato: pochi spostamenti, niente corse' },
    ],
    thread:
      'Base fissa a Cascia (niente valigie da fare e disfare), con la spiritualità di Santa Rita e la Valnerina come cuore, una gita ad Assisi, e le Cascate delle Marmore in chiusura sulla via di casa.',
  },
  places,
  days: [
    {
      date: '2026-08-09',
      weekday: 'Domenica',
      title: 'Arrivo · Santa Rita · Cascia',
      subtitle: 'Giornata soft: siete in viaggio dalla notte.',
      meals: {
        breakfast: { text: 'Lungo il viaggio', included: false },
        lunch: { text: 'Fuori — Trattoria l’Appennino, Cascia', included: false, toOrganize: true },
        dinner: { text: 'In hotel', included: true },
      },
      timeline: [
        {
          time: '~02:45',
          title: 'Partenza da Trani',
          description: 'Di notte le strade sono libere; sosta caffè e carburante in A14.',
        },
        {
          time: '~08:00',
          title: 'Arrivo all’Hotel Delle Rose',
          description: 'Parcheggio gratuito in loco. Colazione, deposito bagagli e richiesta di early check-in.',
          placeRefs: ['hotel-delle-rose'],
        },
        {
          time: 'Mattina',
          title: 'Santuario e Basilica di Santa Rita',
          description:
            'A 20 metri dall’hotel: la storia della Santa è raccontata lungo il percorso di visita a Basilica e Monastero. Cuore spirituale del viaggio; al mattino è fresco e poco affollato.',
          placeRefs: ['basilica-santa-rita'],
        },
        {
          time: 'Pranzo',
          title: 'Pranzo fuori, a Cascia',
          description: 'Trattoria l’Appennino (vedi la sezione ristoranti per l’alternativa).',
          placeRefs: ['trattoria-appennino'],
        },
        {
          time: 'Pomeriggio',
          title: 'Riposo e passeggiata',
          description: 'Riposo nelle ore calde, poi passeggiata tranquilla nel centro storico di Cascia.',
        },
        {
          time: 'Sera',
          title: 'Cena in hotel',
          description: 'Inclusa nella mezza pensione.',
          placeRefs: ['hotel-delle-rose'],
        },
      ],
      parkingNote: 'Hotel (gratuito). Tutto a piedi.',
    },
    {
      date: '2026-08-10',
      weekday: 'Lunedì',
      title: 'Assisi + Santa Maria degli Angeli',
      subtitle: 'Gita in giornata: spirituale + artistica.',
      meals: {
        breakfast: { text: 'In hotel', included: true },
        lunch: { text: 'Fuori — Assisi', included: false, toOrganize: true },
        dinner: { text: 'In hotel', included: true },
      },
      timeline: [
        { time: '~08:00', title: 'Partenza da Cascia', description: '~1h20 di strada verso Santa Maria degli Angeli.' },
        {
          time: '~09:20',
          title: 'Santa Maria degli Angeli',
          description:
            'Basilica, Porziuncola e Cappella del Transito. Parcheggio comodo e pianeggiante in paese. Si fa per prima perché è ai piedi di Assisi.',
          placeRefs: ['santa-maria-degli-angeli'],
        },
        {
          time: '~11:00',
          title: 'Salita ad Assisi',
          description:
            'Parcheggio fuori le mura: Saba Giovanni Paolo II o Mojano. Non entrare in auto nel centro (ZTL).',
          placeRefs: ['parcheggio-saba', 'parcheggio-mojano'],
        },
        {
          time: 'Mattina/pranzo',
          title: 'Basilica di San Francesco',
          description:
            'Basilica Inferiore, Superiore con gli affreschi di Giotto, Tomba del Santo. Poi pranzo fuori ad Assisi.',
          placeRefs: ['basilica-san-francesco'],
        },
        {
          time: 'Pomeriggio',
          title: 'Assisi con calma',
          description:
            'Basilica di Santa Chiara, Cattedrale di San Rufino, Piazza del Comune e Rocca Maggiore per il panorama.',
        },
        { time: '~18:00', title: 'Rientro verso Cascia', description: '~1h30 di strada.' },
        {
          time: '~19:30',
          title: 'Cena in hotel',
          description: 'Inclusa nella mezza pensione.',
          placeRefs: ['hotel-delle-rose'],
        },
      ],
      parkingNote:
        'NON entrare nel centro di Assisi (ZTL con multe). Lasciare l’auto ai parcheggi fuori le mura e salire a piedi o con le scale mobili.',
      note: 'Ipotizzata la cena in hotel per non guidare di notte in montagna. Se preferite serata e cena ad Assisi, si adatta.',
    },
    {
      date: '2026-08-11',
      weekday: 'Martedì',
      title: 'Roccaporena · Norcia · cena speciale',
      isAnniversary: true,
      meals: {
        breakfast: { text: 'In hotel', included: true },
        lunch: { text: 'In hotel (mezza pensione spostata a pranzo)', included: true, toOrganize: true },
        dinner: { text: 'Fuori — Locanda Cacio Re', included: false, toOrganize: true },
      },
      timeline: [
        {
          time: 'Mattina (fresco)',
          title: 'Roccaporena',
          description:
            'Lo Scoglio della Preghiera con la Madonna di bronzo in cima e i luoghi natali di Santa Rita. ~10 minuti d’auto, parcheggio gratuito.',
          placeRefs: ['roccaporena'],
        },
        {
          time: '~13:00',
          title: 'Pranzo in hotel',
          description: 'Mezza pensione spostata a pranzo (da confermare con l’hotel).',
          placeRefs: ['hotel-delle-rose'],
        },
        {
          time: 'Pomeriggio',
          title: 'Norcia',
          description:
            'Piazza San Benedetto, Basilica di San Benedetto (riaperta a ottobre 2025), norcinerie e prodotti tipici. Passeggiata rilassata. ~20 minuti d’auto.',
          placeRefs: ['norcia'],
        },
        {
          time: 'Sera',
          title: 'Cena d’anniversario — Locanda Cacio Re',
          description: 'Trasferimento a Vallo di Nera (~35–40 min). Terrazza con vista sulla valle del Nera.',
          placeRefs: ['locanda-cacio-re'],
        },
        { time: 'Dopo cena', title: 'Rientro a Cascia', description: '~35 minuti.' },
      ],
      parkingNote:
        'Roccaporena gratuito; Norcia fuori le mura (ZTL in centro); Cacio Re parcheggio alla locanda.',
      note: 'Da fare in anticipo: prenotare Cacio Re e chiedere il tavolo in terrazza.',
    },
    {
      date: '2026-08-12',
      weekday: 'Mercoledì',
      title: 'Cascate delle Marmore + rientro',
      meals: {
        breakfast: { text: 'In hotel', included: true },
        lunch: { text: 'Fuori — zona Marmore', included: false, toOrganize: true },
        dinner: { text: 'In viaggio / a casa', included: false },
      },
      timeline: [
        { time: 'Mattina', title: 'Colazione e check-out', description: 'Colazione in hotel, poi check-out.' },
        { time: '~09:00', title: 'Partenza per le Marmore', description: '~1 ora di strada.' },
        {
          time: '~10:00',
          title: 'Cascate delle Marmore',
          description:
            'Arrivo quando parte il rilascio dell’acqua (dalle 10:00). Parcheggio al Belvedere Superiore (o Inferiore). Passeggiata sui sentieri, ~2 ore. Scarpe comode: vicino all’acqua ci si bagna.',
          placeRefs: ['cascate-marmore'],
        },
        {
          time: '~12:30',
          title: 'Pranzo vicino alle cascate',
          description: 'Osteria La Cascata (vedi la sezione ristoranti per l’alternativa).',
          placeRefs: ['osteria-la-cascata'],
        },
        { time: '~13:30', title: 'Partenza per Trani', description: '~5–5h30 di viaggio.' },
        { time: 'Sera', title: 'Arrivo a casa', description: 'Fine del viaggio.' },
      ],
      note:
        'Le Marmore sono verso ovest (Terni), mentre Trani è a sud-est: è un piccolo “giro largo” che allunga un po’ il ritorno. Se non volete un ultimo giorno troppo carico, l’unica alternativa è aggiungere la notte del 12 e rientrare il 13.',
    },
  ],
  restaurantGroups: [
    { title: 'Domenica 9 · pranzo a Cascia', placeIds: ['trattoria-appennino', 'grottino-orlando'] },
    {
      title: 'Lunedì 10 · pranzo ad Assisi',
      placeIds: ['trattoria-pallotta', 'ristorante-san-francesco', 'locanda-del-cardinale'],
    },
    {
      title: 'Martedì 11 · cena d’anniversario',
      placeIds: ['locanda-cacio-re', 'taverna-del-bordone', 'ristorante-vespasia'],
    },
    { title: 'Mercoledì 12 · pranzo alle Marmore', placeIds: ['osteria-la-cascata', 'pavone-doro'] },
  ],
  parkings: [
    { area: 'Cascia (hotel)', solution: 'Hotel Delle Rose, gratuito in loco' },
    { area: 'Roccaporena', solution: 'Parcheggi gratuiti' },
    {
      area: 'Assisi',
      solution:
        'Saba Giovanni Paolo II (coperto, il più vicino a San Francesco) o Mojano (con scale mobili). A pagamento.',
      warning: 'No auto in centro (ZTL)',
      placeRefs: ['parcheggio-saba', 'parcheggio-mojano'],
    },
    { area: 'Santa Maria degli Angeli', solution: 'Ampi parcheggi in paese, pianeggiante e facile' },
    { area: 'Norcia', solution: 'Parcheggi fuori le mura', warning: 'ZTL in centro' },
    { area: 'Vallo di Nera (Cacio Re)', solution: 'Parcheggio alla locanda' },
    { area: 'Cascate delle Marmore', solution: 'Belvedere Superiore (paese di Marmore) o Belvedere Inferiore' },
  ],
  openingHours: [
    {
      place: 'Basilica di Santa Rita (Cascia)',
      hours: 'Apre presto (~6:30–7:00); messe in giornata; Monastero/museo con orari dedicati',
      price: 'Gratuito',
    },
    { place: 'Roccaporena / Scoglio', hours: 'All’aperto, sempre accessibile', price: 'Gratuito' },
    {
      place: 'Santa Maria degli Angeli (Porziuncola)',
      hours: 'Mattina + pomeriggio, con chiusura a pranzo',
      price: 'Gratuito',
    },
    {
      place: 'Basilica di San Francesco (Assisi)',
      hours: 'Inferiore ~6:00–18:45 · Superiore ~8:30–18:45',
      price: 'Gratuito',
    },
    {
      place: 'Cascate delle Marmore',
      hours: 'Agosto: tutti i giorni 9:00–22:30; rilascio acqua 10:00–19:00 e 21:00–22:00',
      price: 'A pagamento (biglietto)',
    },
    {
      place: 'Basilica di San Benedetto (Norcia)',
      hours: 'Orari di apertura della chiesa (riaperta ott. 2025)',
      price: 'Gratuito',
    },
  ],
  hoursDisclaimer: 'Orari indicativi (estate): da riverificare prima della partenza.',
  sitesToCheck: ['santaritadacascia.org', 'cascatadellemarmore.info', 'visit-assisi.it'],
  distances: [
    { from: 'Trani', to: 'Cascia', km: '~450 km', time: '~4h30–5h (di notte più veloce)' },
    { from: 'Cascia', to: 'Assisi', km: '~100 km', time: '~1h30' },
    { from: 'Cascia', to: 'Santa Maria degli Angeli', km: '~95 km', time: '~1h20' },
    { from: 'Cascia', to: 'Roccaporena', km: '~6 km', time: '~10 min' },
    { from: 'Cascia', to: 'Norcia', km: '~18 km', time: '~20 min' },
    { from: 'Cascia', to: 'Vallo di Nera (Cacio Re)', km: '~30 km', time: '~35–40 min' },
    { from: 'Norcia', to: 'Vallo di Nera', km: '—', time: '~40–45 min' },
    { from: 'Cascia', to: 'Cascate delle Marmore', km: '~60 km', time: '~1h' },
    { from: 'Marmore/Terni', to: 'Trani', km: '~450 km', time: '~5–5h30' },
  ],
  practicalNotes: [
    'Prenotare per tempo: agosto è alta stagione e ci si avvicina al Ferragosto. Bloccare cena Cacio Re e biglietti/orari.',
    'Caldo: attività spirituali e passeggiate al mattino presto o nel tardo pomeriggio; ore centrali per riposo o pranzo.',
    'ZTL Assisi: riguarda solo la gita del 10. Lasciare l’auto fuori le mura, mai entrare in centro senza autorizzazione.',
    'Cascate delle Marmore: i sentieri hanno difficoltà diverse; dal Belvedere Superiore ci sono percorsi panoramici facili, altri più impegnativi collegano i livelli. Portare scarpe comode: vicino all’acqua ci si bagna.',
  ],
  toConfirm: [
    'Mezza pensione spostata a pranzo l’11 → confermare con l’Hotel Delle Rose.',
    'Cena del 10 in hotel (ipotesi per evitare la guida notturna) → confermare o cambiare se volete cenare ad Assisi.',
    'Cacio Re aperto martedì 11 → chiamare per conferma + prenotazione terrazza.',
    'Orari dei luoghi → riverificare a ridosso della partenza (possono cambiare in estate).',
    'Rientro: il 12 dopo le Marmore (giornata piena) oppure aggiungere la notte del 12 e rientrare il 13.',
  ],
}

const placesById = new Map(places.map((p) => [p.id, p]))

export function getPlace(id: string): Place | undefined {
  return placesById.get(id)
}
