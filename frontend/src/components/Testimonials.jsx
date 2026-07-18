import { motion } from 'framer-motion'
import { FaQuoteLeft } from 'react-icons/fa'

const testimonials = [
  {
    name: 'Ananya Sharma',
    role: 'Solo traveler · Jaipur & Udaipur',
    quote:
      'WanderAI planned my Rajasthan loop with real palace timings, local thali spots, and a clear ₹ budget. Felt made for Indian trips.',
  },
  {
    name: 'Rahul & Meera',
    role: 'Family trip · Kerala',
    quote:
      'Houseboat, tea gardens, and temple stops all fitted into 5 days. The India map and weather cards helped us dodge monsoon surprises.',
  },
  {
    name: 'Kabir Singh',
    role: 'Adventure · Manali to Leh',
    quote:
      'Loved the mountain-day pacing and packing list. Having everything in Indian Rupees made family approvals easy.',
  },
]

/**
 * India-focused social proof section.
 */
export default function Testimonials() {
  return (
    <section className="border-y border-ink-200/60 bg-white/40 py-20 dark:border-ink-800 dark:bg-ink-900/40">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-saffron-600 dark:text-saffron-400">
            Travelers across India
          </p>
          <h2 className="section-title mt-2">Stories from the road</h2>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {testimonials.map((item, index) => (
            <motion.blockquote
              key={item.name}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08 }}
              className="glass relative p-6"
            >
              <FaQuoteLeft className="mb-4 text-saffron-500/80" />
              <p className="text-sm leading-relaxed text-ink-700 dark:text-ink-200">
                “{item.quote}”
              </p>
              <footer className="mt-5">
                <p className="font-semibold text-ink-900 dark:text-white">{item.name}</p>
                <p className="text-xs text-ink-500">{item.role}</p>
              </footer>
            </motion.blockquote>
          ))}
        </div>
      </div>
    </section>
  )
}
