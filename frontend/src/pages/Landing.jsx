import Hero from '../components/Hero'
import FeatureCards from '../components/FeatureCards'
import IndiaDestinations from '../components/IndiaDestinations'
import Testimonials from '../components/Testimonials'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

/**
 * India-themed marketing landing page.
 */
export default function Landing() {
  return (
    <>
      <Hero />
      <IndiaDestinations />
      <FeatureCards />
      <Testimonials />
      <section className="mx-auto max-w-6xl px-4 py-20 md:px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="glass relative overflow-hidden px-6 py-14 text-center md:px-12"
        >
          <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-saffron-500/20 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-10 -left-10 h-40 w-40 rounded-full bg-brand-500/20 blur-3xl" />
          <h2 className="font-display text-3xl font-semibold text-ink-900 dark:text-white md:text-4xl">
            Ready for your next India adventure?
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-ink-600 dark:text-ink-300">
            Generate a full itinerary in ₹, check weather, explore the India map, and export a PDF —
            all in one place.
          </p>
          <Link to="/planner" className="btn-primary mt-8 inline-flex">
            Open India Trip Planner
          </Link>
        </motion.div>
      </section>
    </>
  )
}
