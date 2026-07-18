import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TripCard from '../components/TripCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import {
  getHistory,
  deleteTrip,
  duplicateTrip,
  reuseTrip,
} from '../services/api'
import { useToast } from '../hooks/useToast'
import { FiSearch } from 'react-icons/fi'

/**
 * Trip history — search, delete, duplicate, and reuse saved plans.
 */
export default function History() {
  const toast = useToast()
  const navigate = useNavigate()
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')

  const load = async (q = '') => {
    setLoading(true)
    try {
      const data = await getHistory(q ? { q } : {})
      setTrips(data.trips || [])
    } catch (err) {
      toast.error(err.message || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    load(query.trim())
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this trip permanently?')) return
    try {
      await deleteTrip(id)
      toast.success('Trip deleted')
      setTrips((prev) => prev.filter((t) => t.id !== id))
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handleDuplicate = async (id) => {
    try {
      const res = await duplicateTrip(id)
      toast.success('Trip duplicated')
      navigate(`/trip/${res.trip.id}`)
    } catch (err) {
      toast.error(err.message)
    }
  }

  const handleReuse = async (id) => {
    try {
      toast.info('Re-generating itinerary with AI…')
      await reuseTrip(id)
      toast.success('Trip refreshed with a new AI plan')
      navigate(`/trip/${id}`)
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-700 dark:text-brand-300">
            History
          </p>
          <h1 className="section-title mt-1">Your saved trips</h1>
        </div>
        <form onSubmit={handleSearch} className="flex w-full max-w-md gap-2">
          <div className="relative flex-1">
            <FiSearch className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
            <input
              className="input-field pl-9"
              placeholder="Search destination or title…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
      </div>

      {loading && <LoadingSkeleton variant="cards" />}

      {!loading && trips.length === 0 && (
        <div className="glass p-10 text-center text-sm text-ink-500">
          No trips yet. Plan one from the Trip Planner and save it here.
        </div>
      )}

      {!loading && trips.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {trips.map((trip) => (
            <TripCard
              key={trip.id}
              trip={trip}
              onDelete={handleDelete}
              onDuplicate={handleDuplicate}
              onReuse={handleReuse}
            />
          ))}
        </div>
      )}
    </div>
  )
}
