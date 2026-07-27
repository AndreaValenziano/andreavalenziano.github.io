import { useState } from 'react'
import type { ReactNode } from 'react'
import { getPlace, trip } from '../data/trip'
import { PlaceActions } from '../components/PlaceActions'
import { ChevronDownIcon, StarIcon } from '../components/icons'
import type { Place } from '../types'

export function InfoTab() {
  const hotel = getPlace(trip.accommodationId)

  return (
    <div className="space-y-3 px-4 pt-4 pb-6">
      <h1 className="font-display text-2xl font-semibold">Informazioni utili</h1>

      <Section title="Hotel" emoji="🏨" defaultOpen>
        {hotel && (
          <div>
            <h3 className="font-display text-lg font-semibold">{hotel.name}</h3>
            {hotel.address && <p className="mt-0.5 text-sm text-pietra-600 dark:text-pietra-400">{hotel.address}</p>}
            {hotel.notes && <p className="mt-2 text-sm leading-relaxed">{hotel.notes}</p>}
            <PlaceActions placeIds={[hotel.id]} />
          </div>
        )}
      </Section>

      <Section title="Ristoranti" emoji="🍽️">
        <div className="space-y-4">
          {trip.restaurantGroups.map((group) => (
            <div key={group.title}>
              <h3 className="text-sm font-bold tracking-wide text-terracotta-700 uppercase dark:text-terracotta-300">
                {group.title}
              </h3>
              <div className="mt-2 space-y-2.5">
                {group.placeIds.map((id) => {
                  const place = getPlace(id)
                  return place ? <RestaurantCard key={id} place={place} /> : null
                })}
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Parcheggi" emoji="🅿️">
        <div className="mb-3 flex gap-2.5 rounded-xl bg-terracotta-50 p-3 text-sm ring-1 ring-terracotta-200 dark:bg-terracotta-900/25 dark:ring-terracotta-800">
          <span aria-hidden="true">⚠️</span>
          <p className="font-medium text-terracotta-800 dark:text-terracotta-100">
            ZTL ad Assisi: mai entrare in auto nel centro storico (multe). Parcheggi fuori le mura.
          </p>
        </div>
        <ul className="space-y-2.5">
          {trip.parkings.map((parking) => (
            <li key={parking.area} className="border-b border-pietra-200 pb-2.5 text-sm last:border-0 last:pb-0 dark:border-pietra-800">
              <span className="font-semibold">{parking.area}</span>
              {parking.warning && (
                <span className="ml-2 rounded-full bg-terracotta-100 px-2 py-0.5 text-[11px] font-bold text-terracotta-700 dark:bg-terracotta-900/50 dark:text-terracotta-200">
                  {parking.warning}
                </span>
              )}
              <p className="mt-0.5 text-pietra-700 dark:text-pietra-300">{parking.solution}</p>
              {parking.placeRefs && <PlaceActions placeIds={parking.placeRefs} />}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Orari dei luoghi" emoji="🕐">
        <p className="mb-3 inline-block rounded-full bg-oro-100 px-3 py-1 text-xs font-bold text-oro-700 dark:bg-oro-900/40 dark:text-oro-200">
          ⚠️ {trip.hoursDisclaimer}
        </p>
        <ul className="space-y-2.5">
          {trip.openingHours.map((row) => (
            <li key={row.place} className="border-b border-pietra-200 pb-2.5 text-sm last:border-0 last:pb-0 dark:border-pietra-800">
              <div className="flex items-start justify-between gap-2">
                <span className="font-semibold">{row.place}</span>
                <span
                  className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold ${
                    row.price === 'Gratuito'
                      ? 'bg-salvia-100 text-salvia-700 dark:bg-salvia-900/50 dark:text-salvia-200'
                      : 'bg-oro-100 text-oro-700 dark:bg-oro-900/40 dark:text-oro-200'
                  }`}
                >
                  {row.price}
                </span>
              </div>
              <p className="mt-0.5 text-pietra-700 dark:text-pietra-300">{row.hours}</p>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-pietra-500 dark:text-pietra-400">
          Siti da controllare:{' '}
          {trip.sitesToCheck.map((site, i) => (
            <span key={site}>
              {i > 0 && ' · '}
              <a href={`https://${site}`} target="_blank" rel="noopener noreferrer" className="underline">
                {site}
              </a>
            </span>
          ))}
        </p>
      </Section>

      <Section title="Distanze e tempi" emoji="🚗">
        <ul className="space-y-2">
          {trip.distances.map((d) => (
            <li
              key={`${d.from}-${d.to}`}
              className="flex items-baseline justify-between gap-3 border-b border-pietra-200 pb-2 text-sm last:border-0 last:pb-0 dark:border-pietra-800"
            >
              <span className="font-medium">
                {d.from} → {d.to}
              </span>
              <span className="shrink-0 text-right text-pietra-600 dark:text-pietra-400">
                {d.km !== '—' && <span>{d.km} · </span>}
                {d.time}
              </span>
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Note pratiche" emoji="💡">
        <ul className="space-y-2.5">
          {trip.practicalNotes.map((note) => (
            <li key={note} className="flex gap-2.5 text-sm leading-relaxed">
              <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-salvia-500" />
              {note}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Da confermare" emoji="✅">
        <ol className="list-decimal space-y-2 pl-5 text-sm leading-relaxed marker:font-bold marker:text-terracotta-600">
          {trip.toConfirm.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
        <p className="mt-3 text-xs text-pietra-500 dark:text-pietra-400">
          Queste voci sono precaricate anche nella Checklist, dove puoi spuntarle.
        </p>
      </Section>
    </div>
  )
}

function Section({
  title,
  emoji,
  defaultOpen = false,
  children,
}: {
  title: string
  emoji: string
  defaultOpen?: boolean
  children: ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <section className="overflow-hidden rounded-2xl bg-pietra-50 shadow-sm dark:bg-pietra-900">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex min-h-13 w-full items-center gap-3 px-4 text-left"
      >
        <span aria-hidden="true">{emoji}</span>
        <span className="font-display flex-1 text-lg font-semibold">{title}</span>
        <ChevronDownIcon className={`size-5 text-pietra-400 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </section>
  )
}

function RestaurantCard({ place }: { place: Place }) {
  return (
    <div
      className={`rounded-xl p-3 ${
        place.alternative
          ? 'bg-pietra-100 ring-1 ring-pietra-200 dark:bg-pietra-950/60 dark:ring-pietra-800'
          : 'bg-pietra-100 ring-1 ring-terracotta-200 dark:bg-pietra-950/60 dark:ring-terracotta-800'
      }`}
    >
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <h4 className="font-semibold">{place.name}</h4>
        {place.rating != null && (
          <span className="inline-flex items-center gap-0.5 text-xs font-bold text-oro-600 dark:text-oro-300">
            <StarIcon className="size-3.5" />
            {place.rating.toLocaleString('it-IT')}
          </span>
        )}
        {place.alternative && (
          <span className="rounded-full bg-pietra-200 px-2 py-0.5 text-[10px] font-bold text-pietra-600 uppercase dark:bg-pietra-800 dark:text-pietra-300">
            Alternativa
          </span>
        )}
      </div>
      {place.address && <p className="mt-0.5 text-xs text-pietra-500 dark:text-pietra-400">{place.address}</p>}
      {place.notes && <p className="mt-1.5 text-sm leading-relaxed">{place.notes}</p>}
      <div className="mt-1 flex flex-wrap items-center gap-x-3 text-xs text-pietra-600 dark:text-pietra-400">
        {place.priceRange && <span>{place.priceRange}</span>}
        {place.phoneDisplay && <span>{place.phoneDisplay}</span>}
      </div>
      <PlaceActions placeIds={[place.id]} />
    </div>
  )
}
