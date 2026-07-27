import type { Place } from '../types'

function isApplePlatform(): boolean {
  const ua = navigator.userAgent
  return /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)
}

/**
 * Link alla mappa nativa: Apple Maps su iOS/iPadOS, Google Maps altrove.
 * Usa le coordinate quando disponibili, altrimenti la query testuale
 * (mapQuery o nome + indirizzo). È l'unica funzione dell'app che richiede rete.
 */
export function mapsUrl(place: Place): string | undefined {
  const hasCoords = place.lat != null && place.lng != null
  const query = place.mapQuery ?? (place.address ? `${place.name}, ${place.address}` : undefined)
  if (!hasCoords && !query) return undefined

  if (isApplePlatform()) {
    const params = new URLSearchParams()
    if (hasCoords) {
      params.set('ll', `${place.lat},${place.lng}`)
      params.set('q', place.name)
    } else {
      params.set('q', query!)
    }
    return `https://maps.apple.com/?${params.toString()}`
  }

  const q = hasCoords ? `${place.lat},${place.lng}` : query!
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`
}

export function telUrl(place: Place): string | undefined {
  return place.phone ? `tel:${place.phone}` : undefined
}
