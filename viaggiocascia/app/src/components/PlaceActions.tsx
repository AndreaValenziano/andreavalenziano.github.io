import { getPlace } from '../data/trip'
import { mapsUrl, telUrl } from '../lib/maps'
import { NavigationIcon, PhoneIcon } from './icons'

interface Props {
  placeIds: string[]
  /** Mostra il nome del luogo accanto ai pulsanti (utile con più luoghi) */
  showNames?: boolean
}

/** Pulsanti "Chiama" e "Portami lì" per i luoghi collegati; nasconde ciò che manca. */
export function PlaceActions({ placeIds, showNames }: Props) {
  const places = placeIds.map(getPlace).filter((p) => p != null)
  if (places.length === 0) return null

  return (
    <div className="mt-2.5 flex flex-col gap-2">
      {places.map((place) => {
        const tel = telUrl(place)
        const map = mapsUrl(place)
        if (!tel && !map) return null
        return (
          <div key={place.id} className="flex flex-wrap items-center gap-2">
            {(showNames || places.length > 1) && (
              <span className="text-sm font-medium text-pietra-700 dark:text-pietra-300">{place.name}</span>
            )}
            {tel && (
              <a
                href={tel}
                className="inline-flex min-h-11 items-center gap-1.5 rounded-full border border-salvia-300 bg-salvia-50 px-4 text-sm font-semibold text-salvia-700 active:bg-salvia-100 dark:border-salvia-700 dark:bg-salvia-900/40 dark:text-salvia-200"
              >
                <PhoneIcon className="size-4" />
                Chiama
              </a>
            )}
            {map && (
              <a
                href={map}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex min-h-11 items-center gap-1.5 rounded-full border border-terracotta-200 bg-terracotta-50 px-4 text-sm font-semibold text-terracotta-700 active:bg-terracotta-100 dark:border-terracotta-800 dark:bg-terracotta-900/30 dark:text-terracotta-200"
              >
                <NavigationIcon className="size-4" />
                Portami lì
              </a>
            )}
          </div>
        )
      })}
    </div>
  )
}
