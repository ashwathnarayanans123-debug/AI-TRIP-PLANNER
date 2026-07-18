import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TripForm from '../components/TripForm'
import ItineraryView from '../components/ItineraryView'
import WeatherCard from '../components/WeatherCard'
import MapView from '../components/MapView'
import BudgetChart from '../components/BudgetChart'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { planTrip, saveTrip, getWeather, getPlaces } from '../services/api'
import { useToast } from '../hooks/useToast'
import { FiSave } from 'react-icons/fi'

/**
 * Main trip planner workspace — form + AI results + weather/maps/budget.
 */
export default function Planner() {
  const toast = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [plan, setPlan] = useState(null)
  const [formSnapshot, setFormSnapshot] = useState(null)
  const [weather, setWeather] = useState(null)
  const [places, setPlaces] = useState(null)
  const [weatherLoading, setWeatherLoading] = useState(false)
  const [placesLoading, setPlacesLoading] = useState(false)

  const handlePlan = async (payload) => {
    setLoading(true)
    setPlan(null)
    setFormSnapshot(payload)
    try {
      const result = await planTrip(payload)
      setPlan(result)
      toast.success('Your AI trip plan is ready!')

      // Enrich with weather + places in parallel — failures are isolated
      setWeatherLoading(true)
      setPlacesLoading(true)

      getWeather(payload.destination)
        .then((w) => setWeather(w))
        .catch(() => toast.info('Weather data unavailable for this destination.'))
        .finally(() => setWeatherLoading(false))

      getPlaces(payload.destination)
        .then((p) => setPlaces(p))
        .catch(() => {}) // places failure is silent — map shows empty state
        .finally(() => setPlacesLoading(false))
    } catch (err) {
      toast.error(err.message || 'Failed to generate trip')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!plan || !formSnapshot) return
    setSaving(true)
    try {
      const response = await saveTrip({
        ...formSnapshot,
        overview: plan.overview,
        itinerary: plan.itinerary,
        estimated_total_budget: plan.estimated_total_budget,
        currency: plan.currency,
        budget_breakdown: plan.budget_breakdown,
        // Now persisted correctly — no longer lost after save
        hotel_recommendations: plan.hotel_recommendations,
        restaurant_suggestions: plan.restaurant_suggestions,
        packing_checklist: plan.packing_checklist,
        safety_tips: plan.safety_tips,
        hidden_gems: plan.hidden_gems,
        travel_hacks: plan.travel_hacks,
        emergency_contacts: plan.emergency_contacts,
      })
      toast.success('Trip saved to history')
      navigate(`/trip/${response.trip.id}`)
    } catch (err) {
      toast.error(err.message || 'Failed to save trip')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-700 dark:text-brand-300">
          Planner
        </p>
        <h1 className="section-title mt-1">Design your next journey</h1>
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
        <TripForm onSubmit={handlePlan} loading={loading} />

        <div className="space-y-5">
          {loading && <LoadingSkeleton />}
          {!loading && plan && (
            <>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="font-display text-2xl font-semibold text-ink-900 dark:text-white">
                  Your AI plan
                  {plan.currency && (
                    <span className="ml-2 text-sm font-normal text-brand-600 dark:text-brand-400">
                      ({plan.currency})
                    </span>
                  )}
                </h2>
                <button
                  type="button"
                  className="btn-primary"
                  onClick={handleSave}
                  disabled={saving}
                >
                  <FiSave /> {saving ? 'Saving…' : 'Save Trip'}
                </button>
              </div>
              <ItineraryView plan={plan} />
              <BudgetChart
                breakdown={plan.budget_breakdown}
                total={plan.estimated_total_budget}
                currency={plan.currency}
              />
              <WeatherCard weather={weather} loading={weatherLoading} />
              <MapView
                destination={formSnapshot?.destination}
                places={places}
                loading={placesLoading}
              />
            </>
          )}
          {!loading && !plan && (
            <div className="glass flex h-full min-h-[280px] items-center justify-center p-8 text-center text-sm text-ink-500">
              Fill in the form and generate a plan to see your itinerary, weather, map, and budget
              analytics here.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
