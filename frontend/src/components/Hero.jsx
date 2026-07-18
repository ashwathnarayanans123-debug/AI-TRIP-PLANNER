import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiArrowRight } from 'react-icons/fi'

/**
 * Full-bleed India-themed hero.
 */
export default function Hero() {
  return (
    <section className="relative min-h-[88vh] overflow-hidden bg-hero-india bg-cover bg-center">
      <div className="absolute inset-0 bg-gradient-to-b from-ink-950/40 via-transparent to-ink-950/80" />
      <div className="relative mx-auto flex min-h-[88vh] max-w-6xl flex-col justify-center px-4 py-20 md:px-6">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-saffron-300"
        >
          India · ₹ budgets · local maps
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="mb-4 font-display text-4xl font-semibold text-white drop-shadow md:text-6xl lg:text-7xl"
        >
          WanderAI
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.12 }}
          className="max-w-3xl font-display text-3xl font-semibold leading-tight text-white md:text-5xl"
        >
          Plan Your Dream India Trip with AI
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="mt-4 max-w-xl text-base text-ink-100/90 md:text-lg"
        >
          From Jaipur to Kerala, Leh to Goa — get day-by-day itineraries, live weather, India maps,
          and budgets in Indian Rupees (₹).
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.38 }}
          className="mt-8 flex flex-wrap gap-3"
        >
          <Link to="/planner" className="btn-primary text-base">
            Plan My India Trip <FiArrowRight />
          </Link>
          <Link
            to="/history"
            className="inline-flex items-center gap-2 rounded-xl border border-white/30 bg-white/10 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur transition hover:bg-white/20"
          >
            My Saved Trips
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
