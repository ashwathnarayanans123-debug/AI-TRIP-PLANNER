import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { INDIAN_DESTINATIONS } from '../data/indianPlaces'

/**
 * Showcase of popular Indian destinations on the landing page.
 */
export default function IndiaDestinations() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-20 md:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-saffron-600 dark:text-saffron-400">
          Explore Bharat
        </p>
        <h2 className="section-title mt-2">Popular places across India</h2>
        <p className="mt-3 text-ink-600 dark:text-ink-300">
          From Rajasthan forts to Kerala backwaters — tap a destination and start planning in ₹.
        </p>
      </div>

      <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {INDIAN_DESTINATIONS.map((place, index) => (
          <motion.div
            key={place.name}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-30px' }}
            transition={{ delay: index * 0.04, duration: 0.4 }}
          >
            <Link
              to="/planner"
              state={{ destination: place.name, starting_location: 'Delhi' }}
              className="group relative block overflow-hidden rounded-2xl"
            >
              <img
                src={place.image}
                alt={place.name}
                className="h-56 w-full object-cover transition duration-500 group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-ink-950/90 via-ink-950/35 to-transparent" />
              <div className="absolute inset-x-0 bottom-0 p-4">
                <p className="font-display text-2xl font-semibold text-white">{place.name}</p>
                <p className="text-xs uppercase tracking-wide text-saffron-300">{place.state}</p>
                <p className="mt-1 text-sm text-ink-200">{place.tagline}</p>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
