import { useState } from 'react'
import { trip } from '../data/trip'
import { daysUntilStart, tripPhase, useRomeNow } from '../lib/dates'
import type { TripPhase } from '../lib/dates'
import { DayView } from './DayView'

type DayViewId = 'overview' | string

function dayNumber(date: string): number {
  return Number(date.slice(8))
}

export function GiorniTab() {
  const now = useRomeNow()
  const phase = tripPhase(now.date)
  const [selected, setSelected] = useState<DayViewId | null>(null)

  const autoView: DayViewId = phase === 'during' ? now.date : 'overview'
  const view = selected ?? autoView
  const selectedDay = trip.days.find((d) => d.date === view)

  return (
    <div className="px-4 pt-4">
      <DayStrip view={view} today={phase === 'during' ? now.date : undefined} onChange={setSelected} />
      {selectedDay ? (
        <DayView day={selectedDay} isToday={phase === 'during' && selectedDay.date === now.date} nowMinutes={now.minutes} />
      ) : (
        <Overview phase={phase} todayIso={now.date} onOpenDay={setSelected} />
      )}
    </div>
  )
}

function DayStrip({
  view,
  today,
  onChange,
}: {
  view: DayViewId
  today?: string
  onChange: (view: DayViewId) => void
}) {
  return (
    <div className="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 pb-1">
      <button
        type="button"
        onClick={() => onChange('overview')}
        className={`min-h-11 shrink-0 rounded-full px-4 text-sm font-semibold transition-colors ${
          view === 'overview'
            ? 'bg-pietra-900 text-pietra-50 dark:bg-pietra-100 dark:text-pietra-900'
            : 'bg-pietra-200/70 text-pietra-700 dark:bg-pietra-800 dark:text-pietra-200'
        }`}
      >
        Panoramica
      </button>
      {trip.days.map((day) => {
        const active = view === day.date
        const isToday = today === day.date
        return (
          <button
            key={day.date}
            type="button"
            onClick={() => onChange(day.date)}
            className={`relative min-h-11 shrink-0 rounded-full px-4 text-sm font-semibold transition-colors ${
              active
                ? day.isAnniversary
                  ? 'bg-oro-500 text-white'
                  : 'bg-terracotta-600 text-white'
                : 'bg-pietra-200/70 text-pietra-700 dark:bg-pietra-800 dark:text-pietra-200'
            }`}
          >
            {day.weekday.slice(0, 3).toLowerCase()} {dayNumber(day.date)}
            {day.isAnniversary && <span className="ml-1">💍</span>}
            {isToday && (
              <span className="absolute -top-0.5 -right-0.5 size-2.5 rounded-full bg-salvia-500 ring-2 ring-pietra-100 dark:ring-pietra-950" />
            )}
          </button>
        )
      })}
    </div>
  )
}

function Overview({
  phase,
  todayIso,
  onOpenDay,
}: {
  phase: TripPhase
  todayIso: string
  onOpenDay: (date: string) => void
}) {
  const remaining = daysUntilStart(todayIso)

  return (
    <div className="mt-3 space-y-4 pb-6">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-terracotta-500 to-terracotta-700 px-5 pt-7 pb-16 text-white shadow-lg">
        <p className="text-sm font-semibold tracking-wide text-terracotta-100 uppercase">9 – 12 agosto 2026</p>
        <h1 className="font-display mt-1 text-3xl leading-tight font-semibold text-balance">
          Umbria — Assisi, Cascia e la Valnerina
        </h1>
        {phase === 'before' && (
          <p className="font-display mt-4 text-xl text-oro-100">
            {remaining === 1 ? 'Si parte domani! 🌅' : (
              <>
                Mancano <span className="text-4xl font-bold text-white">{remaining}</span> giorni
              </>
            )}
          </p>
        )}
        {phase === 'during' && <p className="font-display mt-4 text-xl text-oro-100">Buon viaggio! 🌿</p>}
        {phase === 'after' && (
          <p className="mt-4 inline-block rounded-full bg-white/15 px-3 py-1 text-sm font-semibold">
            Viaggio concluso · archivio dei ricordi
          </p>
        )}
        <svg
          viewBox="0 0 400 60"
          preserveAspectRatio="none"
          aria-hidden="true"
          className="absolute inset-x-0 bottom-0 h-14 w-full"
        >
          <circle cx="330" cy="18" r="16" fill="#f3d98b" opacity="0.9" />
          <path d="M0 38 C 90 8, 180 16, 250 38 C 310 56, 370 46, 400 36 L 400 60 L 0 60 Z" fill="#8a9b73" />
          <path d="M0 50 C 80 34, 210 32, 300 48 C 350 57, 390 52, 400 50 L 400 60 L 0 60 Z" fill="#566546" />
        </svg>
      </section>

      <section className="rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900">
        <h2 className="font-display text-lg font-semibold">Colpo d’occhio</h2>
        <dl className="mt-3 space-y-2.5">
          {trip.overview.facts.map((fact) => (
            <div key={fact.label} className="flex gap-3 text-sm">
              <dt className="w-24 shrink-0 font-semibold text-terracotta-700 dark:text-terracotta-300">{fact.label}</dt>
              <dd className="text-pietra-800 dark:text-pietra-200">{fact.value}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-4 border-t border-pietra-200 pt-3 text-sm leading-relaxed text-pietra-700 italic dark:border-pietra-800 dark:text-pietra-300">
          {trip.overview.thread}
        </p>
      </section>

      <section className="space-y-2.5">
        {trip.days.map((day) => (
          <button
            key={day.date}
            type="button"
            onClick={() => onOpenDay(day.date)}
            className={`flex w-full items-center gap-3 rounded-2xl p-4 text-left shadow-sm transition-colors active:bg-pietra-200 dark:active:bg-pietra-800 ${
              day.isAnniversary
                ? 'bg-oro-50 ring-1 ring-oro-300 dark:bg-oro-900/20 dark:ring-oro-700'
                : 'bg-pietra-50 dark:bg-pietra-900'
            }`}
          >
            <span
              className={`font-display flex size-11 shrink-0 flex-col items-center justify-center rounded-xl text-white ${
                day.isAnniversary ? 'bg-oro-500' : 'bg-terracotta-600'
              }`}
            >
              <span className="text-lg leading-none font-bold">{dayNumber(day.date)}</span>
              <span className="text-[10px] uppercase">ago</span>
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-semibold text-pietra-500 dark:text-pietra-400">
                {day.weekday}
                {day.isAnniversary && ' · anniversario 💍'}
              </span>
              <span className="block truncate font-semibold">{day.title}</span>
            </span>
          </button>
        ))}
      </section>
    </div>
  )
}
