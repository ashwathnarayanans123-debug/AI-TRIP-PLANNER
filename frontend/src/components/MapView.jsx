import { useEffect, useMemo, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix default marker icons when bundling with Vite
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})
L.Marker.prototype.options.icon = DefaultIcon

function colorIcon(hex) {
  const svg = encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="40" viewBox="0 0 28 40">
      <path fill="${hex}" stroke="#fff" stroke-width="2"
        d="M14 1C7.4 1 2 6.4 2 13c0 9.5 12 25 12 25s12-15.5 12-25C26 6.4 20.6 1 14 1z"/>
      <circle cx="14" cy="13" r="5" fill="#fff"/>
    </svg>`,
  )
  return L.icon({
    iconUrl: `data:image/svg+xml,${svg}`,
    iconSize: [28, 40],
    iconAnchor: [14, 40],
    popupAnchor: [0, -36],
  })
}

const ICONS = {
  hotel: colorIcon('#0d9488'),
  restaurant: colorIcon('#d97706'),
  attraction: colorIcon('#0284c7'),
  center: colorIcon('#134e4a'),
}

/**
 * Interactive Leaflet map (OSM tiles) with hotel / restaurant / attraction markers.
 */
export default function MapView({ destination, places, loading }) {
  const mapRef = useRef(null)
  const mapInstance = useRef(null)
  const layerRef = useRef(null)

  const center = places?.center
  const hotels = places?.hotels || []
  const restaurants = places?.restaurants || []
  const attractions = places?.attractions || []

  const directionsUrl = useMemo(() => {
    if (center?.lat && center?.lng) {
      return `https://www.openstreetmap.org/directions?to=${center.lat}%2C${center.lng}`
    }
    return `https://www.openstreetmap.org/search?query=${encodeURIComponent(destination || '')}`
  }, [center, destination])

  // Create map once
  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return

    const map = L.map(mapRef.current).setView([20, 0], 2)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map)

    layerRef.current = L.layerGroup().addTo(map)
    mapInstance.current = map

    // Fix grey tiles when container was hidden / sized after mount
    setTimeout(() => map.invalidateSize(), 80)

    return () => {
      map.remove()
      mapInstance.current = null
      layerRef.current = null
    }
  }, [])

  // Update markers when places change
  useEffect(() => {
    const map = mapInstance.current
    const layer = layerRef.current
    if (!map || !layer) return

    layer.clearLayers()

    const lat = center?.lat
    const lng = center?.lng
    if (lat == null || lng == null) return

    map.setView([lat, lng], 13)
    setTimeout(() => map.invalidateSize(), 50)

    const bounds = []

    const addMarker = (place, type, label) => {
      if (place.lat == null || place.lng == null) return
      const marker = L.marker([place.lat, place.lng], { icon: ICONS[type] || DefaultIcon })
      const bits = [
        `<strong>${place.name}</strong>`,
        label ? `<em>${label}</em>` : '',
        place.address || '',
      ].filter(Boolean)
      marker.bindPopup(bits.join('<br/>'))
      marker.addTo(layer)
      bounds.push([place.lat, place.lng])
    }

    L.marker([lat, lng], { icon: ICONS.center })
      .bindPopup(`<strong>${destination}</strong><br/>Destination center`)
      .addTo(layer)
      .openPopup()
    bounds.push([lat, lng])

    hotels.forEach((p) => addMarker(p, 'hotel', 'Hotel'))
    restaurants.forEach((p) => addMarker(p, 'restaurant', 'Restaurant'))
    attractions.forEach((p) => addMarker(p, 'attraction', 'Attraction'))

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [36, 36], maxZoom: 14 })
    }
  }, [center, destination, hotels, restaurants, attractions])

  if (loading) {
    return (
      <div className="glass p-5">
        <div className="skeleton mb-3 h-6 w-48" />
        <div className="skeleton h-80 w-full" />
      </div>
    )
  }

  if (!destination) {
    return (
      <div className="glass p-5 text-sm text-ink-500">
        Map appears after you generate a trip.
      </div>
    )
  }

  return (
    <section className="glass overflow-hidden p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="font-display text-xl font-semibold text-ink-900 dark:text-white">
            Map — {destination}
          </h3>
          <p className="text-xs text-ink-500">Leaflet · OpenStreetMap · Nominatim / Overpass</p>
        </div>
        <a href={directionsUrl} target="_blank" rel="noreferrer" className="btn-secondary text-xs">
          Open directions
        </a>
      </div>

      <div
        id="map"
        ref={mapRef}
        className="map-frame h-80 w-full overflow-hidden rounded-2xl border border-ink-200/60 dark:border-ink-700"
      />

      <div className="mt-3 flex flex-wrap gap-3 text-[11px] font-medium text-ink-500">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-brand-700" /> Destination
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-brand-500" /> Hotels
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-amber-600" /> Restaurants
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-sky-600" /> Attractions
        </span>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <PlaceList title="Hotels" items={hotels} />
        <PlaceList title="Restaurants" items={restaurants} />
        <PlaceList title="Attractions" items={attractions} />
      </div>
    </section>
  )
}

function PlaceList({ title, items }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">{title}</p>
      <ul className="mt-2 space-y-2">
        {items.length === 0 && <li className="text-xs text-ink-400">No places loaded</li>}
        {items.slice(0, 5).map((place) => (
          <li
            key={place.place_id || `${place.name}-${place.lat}`}
            className="rounded-lg border border-ink-200/60 bg-white/40 px-2.5 py-2 text-xs dark:border-ink-700 dark:bg-ink-900/40"
          >
            <p className="font-medium text-ink-800 dark:text-ink-100">{place.name}</p>
            {place.address && <p className="text-ink-500">{place.address}</p>}
          </li>
        ))}
      </ul>
    </div>
  )
}
