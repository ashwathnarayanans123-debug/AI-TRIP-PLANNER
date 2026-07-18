import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import ItineraryView from '../components/ItineraryView'
import WeatherCard from '../components/WeatherCard'
import MapView from '../components/MapView'
import BudgetChart from '../components/BudgetChart'
import LoadingSkeleton from '../components/LoadingSkeleton'
import {
  getTrip,
  updateTrip,
  deleteTrip,
  duplicateTrip,
  downloadTripPdf,
  getWeather,
  getPlaces,
} from '../services/api'
import { useToast } from '../hooks/useToast'
import { FiArrowLeft, FiDownload, FiCopy, FiTrash2, FiEdit2, FiCheck } from 'react-icons/fi'

function safeParse(raw, fallback) {
  if (!raw) return fallback
  try {
    return JSON.parse(raw)
  } catch {
    return fallback
  }
}

/**
 * Full trip detail — edit title, export PDF, maps, weather, budget.
 */
export default function TripDetail() {
  const { id } = useParams()
  const toast = useToast()
  const navigate = useNavigate()
  const [trip, setTrip] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState('')
  const [weather, setWeather] = useState(null)
  const [places, setPlaces] = useState(null)
  const [weatherLoading, setWeatherLoading] = useState(false)
  const [placesLoading, setPlacesLoading] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const data = await getTrip(id)
        if (cancelled) return
        setTrip(data)
        setTitle(data.title)

        setWeatherLoading(true)
        setPlacesLoading(true)
        getWeather(data.destination)
          .then((w) => !cancelled && setWeather(w))
          .catch(() => {})
          .finally(() => !cancelled && setWeatherLoading(false))
        getPlaces(data.destination)
          .then((p) => !cancelled && setPlaces(p))
          .catch(() => {})
          .finally(() => !cancelled && setPlacesLoading(false))
      } catch (err) {
        toast.error(err.message || 'Trip not found')
        navigate('/history')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const plan = useMemo(() => {
    if (!trip) return null
    return {
      overview: trip.overview,
      itinerary: safeParse(trip.itinerary_json, []),
      // Restore hotel & restaurant lists that were saved with the trip
      hotel_recommendations: safeParse(trip.hotel_recommendations_json, []),
      restaurant_suggestions: safeParse(trip.restaurant_suggestions_json, []),
      packing_checklist: safeParse(trip.packing_checklist_json, []),
      safety_tips: safeParse(trip.safety_tips_json, []),
      hidden_gems: safeParse(trip.hidden_gems_json, []),
      travel_hacks: safeParse(trip.travel_hacks_json, []),
      emergency_contacts: safeParse(trip.emergency_contacts_json, []),
      estimated_total_budget: trip.estimated_total_budget,
      budget_breakdown: safeParse(trip.budget_breakdown_json, null),
      // Use the saved currency — default to INR as the app currency
      currency: trip.currency || 'INR',
    }
  }, [trip])

  const handleSaveTitle = async () => {
    try {
      const updated = await updateTrip(id, { title })
      setTrip(updated)
      setEditing(false)
      toast.success('Trip updated')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this trip?')) return
    try {
      await deleteTrip(id)
      toast.success('Trip deleted')
      navigate('/history')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handleDuplicate = async () => {
    try {
      const res = await duplicateTrip(id)
      toast.success('Duplicated')
      navigate(`/trip/${res.trip.id}`)
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handlePdf = async () => {
    try {
      await downloadTripPdf(id)
      toast.success('PDF download started')
    } catch (err) {
      toast.error(err.message)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
        <LoadingSkeleton />
      </div>
    )
  }

  if (!trip || !plan) return null

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
      <Link
        to="/history"
        className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-ink-500 hover:text-brand-700"
      >
        <FiArrowLeft /> Back to history
      </Link>

      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="flex-1">
          {editing ? (
            <div className="flex flex-wrap gap-2">
              <input
                className="input-field max-w-lg"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <button type="button" className="btn-primary" onClick={handleSaveTitle}>
                <FiCheck /> Save
              </button>
              <button type="button" className="btn-secondary" onClick={() => setEditing(false)}>
                Cancel
              </button>
            </div>
          ) : (
            <>
              <h1 className="section-title">{trip.title}</h1>
              <p className="mt-2 text-sm text-ink-500">
                {trip.starting_location} → {trip.destination} · {trip.number_of_days} days ·{' '}
                {trip.number_of_travelers} travelers
                {trip.currency && (
                  <span className="ml-2 rounded-full bg-brand-100 px-2 py-0.5 text-xs font-semibold text-brand-800 dark:bg-brand-900/40 dark:text-brand-300">
                    {trip.currency}
                  </span>
                )}
              </p>
            </>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-secondary text-xs" onClick={() => setEditing(true)}>
            <FiEdit2 /> Edit
          </button>
          <button type="button" className="btn-secondary text-xs" onClick={handleDuplicate}>
            <FiCopy /> Duplicate
          </button>
          <button type="button" className="btn-primary text-xs" onClick={handlePdf}>
            <FiDownload /> Download PDF
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-xl border border-red-300/60 px-3 py-2 text-xs font-semibold text-red-600 dark:border-red-800 dark:text-red-300"
            onClick={handleDelete}
          >
            <FiTrash2 /> Delete
          </button>
        </div>
      </div>

      <div className="space-y-5">
        <ItineraryView plan={plan} />
        <BudgetChart
          breakdown={plan.budget_breakdown}
          total={plan.estimated_total_budget}
          currency={plan.currency}
        />
        <WeatherCard weather={weather} loading={weatherLoading} />
        <MapView destination={trip.destination} places={places} loading={placesLoading} />
      </div>
    </div>
  )
}
