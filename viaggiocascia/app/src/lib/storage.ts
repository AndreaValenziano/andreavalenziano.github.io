import { useEffect, useState } from 'react'
import { romeNow } from './dates'

const PREFIX = 'viaggiocascia.v1.'

/** Chiavi che costituiscono i dati personali (export/import/reset). */
const USER_DATA_KEYS = ['checklist', 'expenses', 'notes'] as const

export function useStoredState<T>(key: string, initial: T | (() => T)) {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = localStorage.getItem(PREFIX + key)
      if (raw != null) return JSON.parse(raw) as T
    } catch {
      // valore corrotto: si riparte dal default
    }
    return typeof initial === 'function' ? (initial as () => T)() : initial
  })

  useEffect(() => {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value))
    } catch {
      // storage pieno o non disponibile: l'app continua a funzionare in memoria
    }
  }, [key, value])

  return [value, setValue] as const
}

export function exportUserData(): { filename: string; json: string } {
  const data: Record<string, unknown> = {}
  for (const key of USER_DATA_KEYS) {
    const raw = localStorage.getItem(PREFIX + key)
    if (raw != null) {
      try {
        data[key] = JSON.parse(raw)
      } catch {
        // chiave corrotta: esclusa dal backup
      }
    }
  }
  const payload = { app: 'viaggiocascia', version: 1, exportedAt: new Date().toISOString(), data }
  return {
    filename: `umbria2026-dati-${romeNow().date}.json`,
    json: JSON.stringify(payload, null, 2),
  }
}

/** Importa un backup JSON. Lancia un errore (messaggio in italiano) se il file non è valido. */
export function importUserData(json: string): void {
  let parsed: unknown
  try {
    parsed = JSON.parse(json)
  } catch {
    throw new Error('Il file non è un JSON valido.')
  }
  const payload = parsed as { app?: string; data?: Record<string, unknown> }
  if (payload?.app !== 'viaggiocascia' || typeof payload.data !== 'object' || payload.data == null) {
    throw new Error('Il file non sembra un backup di questa app.')
  }
  for (const key of USER_DATA_KEYS) {
    if (key in payload.data) {
      localStorage.setItem(PREFIX + key, JSON.stringify(payload.data[key]))
    }
  }
}

export function resetUserData(): void {
  for (const key of USER_DATA_KEYS) {
    localStorage.removeItem(PREFIX + key)
  }
}

export const euro = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' })
