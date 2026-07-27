export type PlaceCategory = 'hotel' | 'restaurant' | 'sight' | 'parking'

export interface Place {
  id: string
  name: string
  category: PlaceCategory
  address?: string
  /** Numero in formato E.164, usato per il link tel: */
  phone?: string
  /** Numero leggibile da mostrare in UI */
  phoneDisplay?: string
  lat?: number
  lng?: number
  /** Query testuale per la mappa quando mancano le coordinate (dati dal markdown, mai inventati) */
  mapQuery?: string
  rating?: number
  notes?: string
  priceRange?: string
  /** Giorno/pasto di riferimento (ristoranti) */
  when?: string
  /** Alternativa rispetto alla scelta principale */
  alternative?: boolean
}

export interface Meal {
  text: string
  /** Incluso nella mezza pensione dell'hotel */
  included: boolean
  /** In grassetto nel piano pasti: da organizzare/prenotare */
  toOrganize?: boolean
}

export interface Stop {
  time: string
  title: string
  description: string
  placeRefs?: string[]
}

export interface Day {
  date: string
  weekday: string
  title: string
  subtitle?: string
  isAnniversary?: boolean
  meals: { breakfast: Meal; lunch: Meal; dinner: Meal }
  timeline: Stop[]
  parkingNote?: string
  note?: string
}

export interface Parking {
  area: string
  solution: string
  warning?: string
  placeRefs?: string[]
}

export interface OpeningHour {
  place: string
  hours: string
  price: string
}

export interface Distance {
  from: string
  to: string
  km: string
  time: string
}

export interface Trip {
  title: string
  subtitle: string
  startDate: string
  endDate: string
  timezone: 'Europe/Rome'
  overview: { facts: { label: string; value: string }[]; thread: string }
  accommodationId: string
  places: Place[]
  days: Day[]
  restaurantGroups: { title: string; placeIds: string[] }[]
  parkings: Parking[]
  openingHours: OpeningHour[]
  hoursDisclaimer: string
  sitesToCheck: string[]
  distances: Distance[]
  practicalNotes: string[]
  toConfirm: string[]
}

/* ---- Dati utente (localStorage) ---- */

export type ChecklistCategory = 'valigia' | 'prenotazioni' | 'promemoria'

export interface ChecklistItem {
  id: string
  category: ChecklistCategory
  text: string
  done: boolean
}

export interface Expense {
  id: string
  description: string
  amount: number
  /** 'pre' oppure la data ISO di uno dei giorni del viaggio */
  day: string
  category?: string
}

export type NotesMap = Record<string, string>
