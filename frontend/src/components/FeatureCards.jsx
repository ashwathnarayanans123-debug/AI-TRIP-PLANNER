import { motion } from 'framer-motion'
import { FiCpu, FiCloud, FiMap, FiPieChart, FiFileText, FiShield } from 'react-icons/fi'

const features = [
  {
    icon: FiCpu,
    title: 'India-first AI plans',
    desc: 'Day-by-day itineraries for Jaipur, Goa, Kerala, Leh, and more — tuned to Indian travel styles.',
  },
  {
    icon: FiCloud,
    title: 'Local weather',
    desc: 'Live temperature, humidity, wind, and rain chances for Indian cities before you pack.',
  },
  {
    icon: FiMap,
    title: 'India map & places',
    desc: 'Leaflet map centered on India with hotels, restaurants, and attractions from OpenStreetMap.',
  },
  {
    icon: FiPieChart,
    title: 'Budgets in ₹',
    desc: 'See stays, food, trains, flights, tickets, and shopping broken down in Indian Rupees.',
  },
  {
    icon: FiFileText,
    title: 'PDF for the road',
    desc: 'Download a clean itinerary PDF to share with family before you leave.',
  },
  {
    icon: FiShield,
    title: 'Travel-ready tips',
    desc: 'Packing lists, safety notes, hidden gems, and Indian emergency contacts in every plan.',
  },
]

/**
 * Feature highlight grid for the India landing page.
 */
export default function FeatureCards() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-20 md:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-saffron-600 dark:text-saffron-400">
          Why WanderAI India
        </p>
        <h2 className="section-title mt-2">Built for journeys across Bharat</h2>
        <p className="mt-3 text-ink-600 dark:text-ink-300">
          AI itineraries, India maps, live weather, and rupee budgets — one premium planning flow.
        </p>
      </div>

      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((feature, index) => (
          <motion.article
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ delay: index * 0.06, duration: 0.45 }}
            className="glass p-6 transition hover:-translate-y-1 hover:shadow-glass-lg"
          >
            <div className="mb-4 inline-flex rounded-xl bg-brand-500/15 p-3 text-brand-700 dark:text-brand-300">
              <feature.icon size={22} />
            </div>
            <h3 className="text-lg font-semibold text-ink-900 dark:text-white">{feature.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-600 dark:text-ink-300">
              {feature.desc}
            </p>
          </motion.article>
        ))}
      </div>
    </section>
  )
}
