import { Link } from 'react-router-dom'
import { FiCopy, FiTrash2, FiEye, FiRefreshCw } from 'react-icons/fi'

/**
 * Card for a saved trip in history lists.
 */
export default function TripCard({ trip, onDelete, onDuplicate, onReuse }) {
  return (
    <article className="glass flex flex-col justify-between p-5 transition hover:-translate-y-0.5 hover:shadow-glass-lg">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-300">
          {trip.number_of_days} days · {trip.budget} · {trip.transportation}
        </p>
        <h3 className="mt-1 font-display text-xl font-semibold text-ink-900 dark:text-white">
          {trip.title}
        </h3>
        <p className="mt-1 text-sm text-ink-500">
          {trip.starting_location} → {trip.destination}
        </p>
        {trip.estimated_total_budget != null && (
          <p className="mt-3 text-sm font-semibold text-ink-800 dark:text-ink-100">
            Est. ₹ {Number(trip.estimated_total_budget).toLocaleString()}
          </p>
        )}
        <p className="mt-1 text-xs text-ink-400">
          Updated {new Date(trip.updated_at).toLocaleDateString()}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link to={`/trip/${trip.id}`} className="btn-secondary text-xs">
          <FiEye /> View
        </Link>
        {onDuplicate && (
          <button type="button" className="btn-secondary text-xs" onClick={() => onDuplicate(trip.id)}>
            <FiCopy /> Duplicate
          </button>
        )}
        {onReuse && (
          <button type="button" className="btn-secondary text-xs" onClick={() => onReuse(trip.id)}>
            <FiRefreshCw /> Reuse
          </button>
        )}
        {onDelete && (
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-xl border border-red-300/60 px-3 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-50 dark:border-red-800 dark:text-red-300 dark:hover:bg-red-950/40"
            onClick={() => onDelete(trip.id)}
          >
            <FiTrash2 /> Delete
          </button>
        )}
      </div>
    </article>
  )
}
