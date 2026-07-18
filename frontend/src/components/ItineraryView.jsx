import { motion } from 'framer-motion'
import { FiSunrise, FiSun, FiMoon, FiMapPin, FiCoffee } from 'react-icons/fi'

function Segment({ icon: Icon, label, data, currency = 'INR' }) {
  if (!data) return null
  return (
    <div className="rounded-xl border border-ink-200/70 bg-white/50 p-4 dark:border-ink-700 dark:bg-ink-900/40">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-brand-700 dark:text-brand-300">
        <Icon /> {label}
      </div>
      <p className="text-sm text-ink-800 dark:text-ink-100">{data.activity}</p>
      <div className="mt-2 space-y-1 text-xs text-ink-500 dark:text-ink-400">
        {data.place && (
          <p className="flex items-center gap-1">
            <FiMapPin /> {data.place}
          </p>
        )}
        {data.restaurant && (
          <p className="flex items-center gap-1">
            <FiCoffee /> {data.restaurant}
          </p>
        )}
        {data.local_transport && <p>Transport: {data.local_transport}</p>}
        {data.best_visiting_time && <p>Best time: {data.best_visiting_time}</p>}
        {data.estimated_cost != null && (
          <p>
            Est. cost: {currency}{' '}
            {Number(data.estimated_cost).toLocaleString(undefined, {
              maximumFractionDigits: 0,
            })}
          </p>
        )}
        {data.notes && <p className="italic">{data.notes}</p>}
      </div>
    </div>
  )
}

/**
 * Renders the AI itinerary overview and day-by-day plan.
 */
export default function ItineraryView({ plan }) {
  if (!plan) return null
  const currency = plan.currency || 'INR'

  return (
    <div className="space-y-6">
      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass p-6"
      >
        <h3 className="font-display text-2xl font-semibold text-ink-900 dark:text-white">
          Trip Overview
        </h3>
        <p className="mt-3 text-sm leading-relaxed text-ink-700 dark:text-ink-200">
          {plan.overview}
        </p>
        <p className="mt-4 text-lg font-semibold text-brand-700 dark:text-brand-300">
          Estimated total: {currency}{' '}
          {Number(plan.estimated_total_budget || 0).toLocaleString(undefined, {
            maximumFractionDigits: 0,
          })}
        </p>
      </motion.section>

      <div className="space-y-4">
        {(plan.itinerary || []).map((day, index) => (
          <motion.article
            key={day.day || index}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="glass p-5 md:p-6"
          >
            <h4 className="font-display text-xl font-semibold text-ink-900 dark:text-white">
              Day {day.day}
              {day.title ? `: ${day.title}` : ''}
            </h4>
            {day.hotel && (
              <p className="mt-1 text-sm text-ink-500">Stay: {day.hotel}</p>
            )}
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              <Segment icon={FiSunrise} label="Morning" data={day.morning} currency={currency} />
              <Segment icon={FiSun} label="Afternoon" data={day.afternoon} currency={currency} />
              <Segment icon={FiMoon} label="Evening" data={day.evening} currency={currency} />
            </div>
            {day.nearby_attractions?.length > 0 && (
              <p className="mt-3 text-xs text-ink-500">
                Nearby: {day.nearby_attractions.join(' · ')}
              </p>
            )}
          </motion.article>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {[
          ['Hotel recommendations', plan.hotel_recommendations],
          ['Restaurant suggestions', plan.restaurant_suggestions],
          ['Packing checklist', plan.packing_checklist],
          ['Safety tips', plan.safety_tips],
          ['Hidden gems', plan.hidden_gems],
          ['Travel hacks', plan.travel_hacks],
        ].map(([title, items]) =>
          items?.length ? (
            <section key={title} className="glass p-5">
              <h4 className="font-semibold text-ink-900 dark:text-white">{title}</h4>
              <ul className="mt-3 space-y-1.5 text-sm text-ink-600 dark:text-ink-300">
                {items.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </section>
          ) : null,
        )}
      </div>

      {plan.emergency_contacts?.length > 0 && (
        <section className="glass p-5">
          <h4 className="font-semibold text-ink-900 dark:text-white">Emergency contacts</h4>
          <ul className="mt-3 space-y-2 text-sm text-ink-600 dark:text-ink-300">
            {plan.emergency_contacts.map((c, i) => (
              <li key={`${c.name}-${i}`}>
                <span className="font-medium text-ink-800 dark:text-ink-100">{c.name}</span>
                {c.phone ? ` — ${c.phone}` : ''}
                {c.notes ? ` (${c.notes})` : ''}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
