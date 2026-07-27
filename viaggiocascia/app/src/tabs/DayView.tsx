import { nearestStopIndex } from '../lib/dates'
import { PlaceActions } from '../components/PlaceActions'
import type { Day, Meal } from '../types'

const longDate = new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'long', timeZone: 'Europe/Rome' })

export function DayView({ day, isToday, nowMinutes }: { day: Day; isToday: boolean; nowMinutes: number }) {
  const currentIndex = isToday ? nearestStopIndex(day.timeline, nowMinutes) : -1

  return (
    <div className="mt-3 space-y-4 pb-6">
      <header
        className={`rounded-2xl p-4 shadow-sm ${
          day.isAnniversary
            ? 'bg-gradient-to-br from-oro-50 to-terracotta-50 ring-1 ring-oro-300 dark:from-oro-900/25 dark:to-terracotta-900/20 dark:ring-oro-700'
            : 'bg-pietra-50 dark:bg-pietra-900'
        }`}
      >
        <p className="text-sm font-semibold tracking-wide text-terracotta-700 uppercase dark:text-terracotta-300">
          {day.weekday} {longDate.format(new Date(`${day.date}T12:00:00`))}
          {isToday && <span className="ml-2 rounded-full bg-salvia-500 px-2 py-0.5 text-[11px] text-white">Oggi</span>}
        </p>
        <h1 className="font-display mt-1 text-2xl leading-tight font-semibold">{day.title}</h1>
        {day.isAnniversary && (
          <p className="mt-1.5 font-medium text-oro-700 dark:text-oro-300">💍 Il vostro anniversario</p>
        )}
        {day.subtitle && <p className="mt-1 text-sm text-pietra-600 italic dark:text-pietra-400">{day.subtitle}</p>}
      </header>

      <section className="grid grid-cols-3 gap-2">
        <MealCard label="Colazione" meal={day.meals.breakfast} />
        <MealCard label="Pranzo" meal={day.meals.lunch} />
        <MealCard label="Cena" meal={day.meals.dinner} />
      </section>

      <ol className="relative ml-1 space-y-3 border-l-2 border-pietra-300 pl-5 dark:border-pietra-700">
        {day.timeline.map((stop, i) => {
          const current = i === currentIndex
          return (
            <li key={`${stop.time}-${stop.title}`} className="relative">
              <span
                className={`absolute top-4 -left-[27px] size-3.5 rounded-full border-2 ${
                  current
                    ? 'border-terracotta-500 bg-terracotta-500 ring-4 ring-terracotta-200 dark:ring-terracotta-900'
                    : 'border-pietra-400 bg-pietra-100 dark:border-pietra-600 dark:bg-pietra-950'
                }`}
              />
              <div
                className={`rounded-2xl p-3.5 shadow-sm ${
                  current
                    ? 'bg-terracotta-50 ring-2 ring-terracotta-400 dark:bg-terracotta-900/25 dark:ring-terracotta-600'
                    : 'bg-pietra-50 dark:bg-pietra-900'
                }`}
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-xs font-bold tracking-wide text-salvia-600 uppercase dark:text-salvia-300">
                    {stop.time}
                  </span>
                  {current && (
                    <span className="rounded-full bg-terracotta-600 px-2 py-0.5 text-[11px] font-bold text-white">
                      Adesso
                    </span>
                  )}
                </div>
                <h3 className="mt-0.5 font-semibold">{stop.title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-pietra-700 dark:text-pietra-300">{stop.description}</p>
                {stop.placeRefs && <PlaceActions placeIds={stop.placeRefs} />}
              </div>
            </li>
          )
        })}
      </ol>

      {day.parkingNote && (
        <aside className="flex gap-3 rounded-2xl bg-oro-50 p-4 text-sm ring-1 ring-oro-200 dark:bg-oro-900/20 dark:ring-oro-800">
          <span aria-hidden="true">🅿️</span>
          <p className="leading-relaxed text-oro-800 dark:text-oro-100">{day.parkingNote}</p>
        </aside>
      )}
      {day.note && (
        <aside className="rounded-2xl bg-pietra-50 p-4 text-sm leading-relaxed text-pietra-700 shadow-sm dark:bg-pietra-900 dark:text-pietra-300">
          <span className="font-semibold text-pietra-900 dark:text-pietra-100">Nota · </span>
          {day.note}
        </aside>
      )}
    </div>
  )
}

function MealCard({ label, meal }: { label: string; meal: Meal }) {
  return (
    <div className="flex flex-col rounded-2xl bg-pietra-50 p-2.5 shadow-sm dark:bg-pietra-900">
      <span className="text-[11px] font-bold tracking-wide text-pietra-500 uppercase dark:text-pietra-400">{label}</span>
      <span className="mt-0.5 flex-1 text-[13px] leading-snug font-medium">{meal.text}</span>
      {meal.included ? (
        <span className="mt-1.5 self-start rounded-full bg-salvia-100 px-2 py-0.5 text-[10px] font-bold text-salvia-700 dark:bg-salvia-900/50 dark:text-salvia-200">
          Mezza pensione
        </span>
      ) : meal.toOrganize ? (
        <span className="mt-1.5 self-start rounded-full bg-oro-100 px-2 py-0.5 text-[10px] font-bold text-oro-700 dark:bg-oro-900/40 dark:text-oro-200">
          Da organizzare
        </span>
      ) : null}
    </div>
  )
}
