import { useEffect, useState } from 'react'
import { trip } from '../data/trip'
import type { Stop } from '../types'

export interface RomeNow {
  /** Data ISO (YYYY-MM-DD) nel fuso Europe/Rome */
  date: string
  /** Minuti trascorsi dalla mezzanotte, nel fuso Europe/Rome */
  minutes: number
}

export function romeNow(now: Date = new Date()): RomeNow {
  // Il locale sv-SE produce direttamente "YYYY-MM-DD HH:mm"
  const formatted = new Intl.DateTimeFormat('sv-SE', {
    timeZone: trip.timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).format(now)
  const [date, hm] = formatted.split(' ')
  const [h, m] = hm.split(':')
  return { date, minutes: Number(h) * 60 + Number(m) }
}

export function useRomeNow(): RomeNow {
  const [now, setNow] = useState<RomeNow>(() => romeNow())
  useEffect(() => {
    const id = setInterval(() => setNow(romeNow()), 30_000)
    return () => clearInterval(id)
  }, [])
  return now
}

export type TripPhase = 'before' | 'during' | 'after'

export function tripPhase(date: string): TripPhase {
  if (date < trip.startDate) return 'before'
  if (date > trip.endDate) return 'after'
  return 'during'
}

export function daysUntilStart(date: string): number {
  return Math.round((Date.parse(trip.startDate) - Date.parse(date)) / 86_400_000)
}

const KEYWORD_MINUTES: [RegExp, number][] = [
  [/dopo cena/, 22 * 60],
  [/mattina\/pranzo/, 11 * 60 + 30],
  [/mattina/, 9 * 60],
  [/pranzo/, 13 * 60],
  [/pomeriggio/, 16 * 60],
  [/sera/, 20 * 60],
]

/** Ora approssimata di una tappa, in minuti: "~08:00" → 480, "Pomeriggio" → 960. */
export function stopMinutes(time: string): number | undefined {
  const explicit = time.match(/(\d{1,2})[:.](\d{2})/)
  if (explicit) return Number(explicit[1]) * 60 + Number(explicit[2])
  const t = time.toLowerCase()
  return KEYWORD_MINUTES.find(([re]) => re.test(t))?.[1]
}

/** Indice della tappa più vicina all'ora attuale (-1 se nessuna tappa ha un orario). */
export function nearestStopIndex(stops: Stop[], minutes: number): number {
  let best = -1
  let bestDist = Infinity
  stops.forEach((stop, i) => {
    const m = stopMinutes(stop.time)
    if (m == null) return
    const dist = Math.abs(m - minutes)
    if (dist < bestDist) {
      best = i
      bestDist = dist
    }
  })
  return best
}
