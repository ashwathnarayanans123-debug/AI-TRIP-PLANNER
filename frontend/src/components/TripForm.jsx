import { useState } from 'react'
import { motion } from 'framer-motion'

const INTERESTS = [
  'Adventure',
  'Mountains',
  'Beaches',
  'Nature',
  'Wildlife',
  'Shopping',
  'Food',
  'Temples',
  'History',
  'Museums',
  'Nightlife',
  'Photography',
]

const initialForm = {
  starting_location: '',
  destination: '',
  start_date: '',
  end_date: '',
  number_of_days: 5,
  number_of_travelers: 2,
  budget: 'medium',
  transportation: 'flight',
  hotel_type: 'standard',
  interests: [],
  additional_notes: '',
}

/**
 * Collects trip preferences and validates before submitting to the AI planner.
 */
export default function TripForm({ onSubmit, loading = false, initialValues = null }) {
  const [form, setForm] = useState({ ...initialForm, ...(initialValues || {}) })
  const [errors, setErrors] = useState({})

  const setField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  const toggleInterest = (interest) => {
    const key = interest.toLowerCase()
    setForm((prev) => {
      const exists = prev.interests.includes(key)
      return {
        ...prev,
        interests: exists
          ? prev.interests.filter((i) => i !== key)
          : [...prev.interests, key],
      }
    })
  }

  const validate = () => {
    const next = {}
    if (!form.starting_location.trim()) next.starting_location = 'Starting location is required'
    if (!form.destination.trim()) next.destination = 'Destination is required'
    if (form.number_of_days < 1 || form.number_of_days > 30) {
      next.number_of_days = 'Days must be between 1 and 30'
    }
    if (form.number_of_travelers < 1) next.number_of_travelers = 'At least 1 traveler'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return
    onSubmit({
      ...form,
      starting_location: form.starting_location.trim(),
      destination: form.destination.trim(),
      number_of_days: Number(form.number_of_days),
      number_of_travelers: Number(form.number_of_travelers),
      start_date: form.start_date || null,
      end_date: form.end_date || null,
      additional_notes: form.additional_notes || null,
    })
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass space-y-6 p-6 md:p-8"
    >
      <div>
        <h2 className="font-display text-2xl font-semibold text-ink-900 dark:text-white">
          Trip details
        </h2>
        <p className="mt-1 text-sm text-ink-500">
          Tell WanderAI where you&apos;re going — we&apos;ll craft the rest.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="label-field" htmlFor="starting_location">
            Starting Location
          </label>
          <input
            id="starting_location"
            className="input-field"
            value={form.starting_location}
            onChange={(e) => setField('starting_location', e.target.value)}
            placeholder="e.g. New York"
          />
          {errors.starting_location && (
            <p className="mt-1 text-xs text-red-500">{errors.starting_location}</p>
          )}
        </div>
        <div>
          <label className="label-field" htmlFor="destination">
            Destination
          </label>
          <input
            id="destination"
            className="input-field"
            value={form.destination}
            onChange={(e) => setField('destination', e.target.value)}
            placeholder="e.g. Tokyo"
          />
          {errors.destination && (
            <p className="mt-1 text-xs text-red-500">{errors.destination}</p>
          )}
        </div>
        <div>
          <label className="label-field" htmlFor="start_date">
            Travel Start Date
          </label>
          <input
            id="start_date"
            type="date"
            className="input-field"
            value={form.start_date}
            onChange={(e) => setField('start_date', e.target.value)}
          />
        </div>
        <div>
          <label className="label-field" htmlFor="end_date">
            Travel End Date
          </label>
          <input
            id="end_date"
            type="date"
            className="input-field"
            value={form.end_date}
            onChange={(e) => setField('end_date', e.target.value)}
          />
        </div>
        <div>
          <label className="label-field" htmlFor="number_of_days">
            Number of Days
          </label>
          <input
            id="number_of_days"
            type="number"
            min={1}
            max={30}
            className="input-field"
            value={form.number_of_days}
            onChange={(e) => setField('number_of_days', e.target.value)}
          />
          {errors.number_of_days && (
            <p className="mt-1 text-xs text-red-500">{errors.number_of_days}</p>
          )}
        </div>
        <div>
          <label className="label-field" htmlFor="number_of_travelers">
            Number of Travelers
          </label>
          <input
            id="number_of_travelers"
            type="number"
            min={1}
            max={50}
            className="input-field"
            value={form.number_of_travelers}
            onChange={(e) => setField('number_of_travelers', e.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="label-field" htmlFor="budget">
            Budget
          </label>
          <select
            id="budget"
            className="input-field"
            value={form.budget}
            onChange={(e) => setField('budget', e.target.value)}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="luxury">Luxury</option>
          </select>
        </div>
        <div>
          <label className="label-field" htmlFor="transportation">
            Transportation
          </label>
          <select
            id="transportation"
            className="input-field"
            value={form.transportation}
            onChange={(e) => setField('transportation', e.target.value)}
          >
            <option value="car">Car</option>
            <option value="flight">Flight</option>
            <option value="train">Train</option>
            <option value="bus">Bus</option>
          </select>
        </div>
        <div>
          <label className="label-field" htmlFor="hotel_type">
            Hotel Type
          </label>
          <select
            id="hotel_type"
            className="input-field"
            value={form.hotel_type}
            onChange={(e) => setField('hotel_type', e.target.value)}
          >
            <option value="budget">Budget</option>
            <option value="standard">Standard</option>
            <option value="premium">Premium</option>
          </select>
        </div>
      </div>

      <div>
        <p className="label-field">Interests</p>
        <div className="flex flex-wrap gap-2">
          {INTERESTS.map((interest) => {
            const active = form.interests.includes(interest.toLowerCase())
            return (
              <button
                key={interest}
                type="button"
                onClick={() => toggleInterest(interest)}
                className={`rounded-xl border px-3 py-1.5 text-xs font-semibold transition ${
                  active
                    ? 'border-brand-500 bg-brand-500/15 text-brand-800 dark:text-brand-200'
                    : 'border-ink-200 text-ink-600 hover:border-brand-400 dark:border-ink-700 dark:text-ink-300'
                }`}
              >
                {interest}
              </button>
            )
          })}
        </div>
      </div>

      <div>
        <label className="label-field" htmlFor="additional_notes">
          Additional Notes
        </label>
        <textarea
          id="additional_notes"
          rows={3}
          className="input-field resize-y"
          value={form.additional_notes}
          onChange={(e) => setField('additional_notes', e.target.value)}
          placeholder="Dietary needs, must-see spots, mobility notes…"
        />
      </div>

      <button type="submit" className="btn-primary w-full md:w-auto" disabled={loading}>
        {loading ? 'Generating your trip…' : 'Generate AI Trip Plan'}
      </button>
    </motion.form>
  )
}
