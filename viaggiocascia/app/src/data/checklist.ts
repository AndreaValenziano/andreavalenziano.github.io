import type { ChecklistCategory, ChecklistItem } from '../types'

export const CHECKLIST_CATEGORIES: { id: ChecklistCategory; label: string; emoji: string }[] = [
  { id: 'prenotazioni', label: 'Prenotazioni da fare', emoji: '📞' },
  { id: 'valigia', label: 'Valigia', emoji: '🧳' },
  { id: 'promemoria', label: 'Da non dimenticare', emoji: '📌' },
]

/** Voci precaricate, ricavate dalla sezione "Da confermare" e dalle note dell'itinerario. */
export const initialChecklist: ChecklistItem[] = [
  {
    id: 'seed-cacio-re',
    category: 'prenotazioni',
    text: 'Prenotare la cena d’anniversario alla Locanda Cacio Re (mar 11) e chiedere il tavolo in terrazza',
    done: false,
  },
  {
    id: 'seed-mezza-pensione',
    category: 'prenotazioni',
    text: 'Confermare con l’Hotel Delle Rose la mezza pensione spostata a pranzo per martedì 11',
    done: false,
  },
  {
    id: 'seed-early-checkin',
    category: 'prenotazioni',
    text: 'Chiedere all’hotel l’early check-in per domenica 9',
    done: false,
  },
  {
    id: 'seed-cena-10',
    category: 'prenotazioni',
    text: 'Decidere la cena del 10: in hotel (ipotesi attuale) oppure serata ad Assisi',
    done: false,
  },
  {
    id: 'seed-biglietti-marmore',
    category: 'prenotazioni',
    text: 'Biglietti e orari d’ingresso alle Cascate delle Marmore',
    done: false,
  },
  {
    id: 'seed-orari',
    category: 'prenotazioni',
    text: 'Riverificare gli orari dei luoghi a ridosso della partenza',
    done: false,
  },
  {
    id: 'seed-rientro',
    category: 'prenotazioni',
    text: 'Decidere il rientro: mercoledì 12 dopo le Marmore oppure notte extra e rientro il 13',
    done: false,
  },
  {
    id: 'seed-scarpe',
    category: 'valigia',
    text: 'Scarpe comode per i sentieri delle Marmore (vicino all’acqua ci si bagna)',
    done: false,
  },
]
