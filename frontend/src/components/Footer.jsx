import { Link } from 'react-router-dom'
import { FiGithub, FiMail, FiMapPin } from 'react-icons/fi'

/**
 * Site footer with brand, links, and contact strip.
 */
export default function Footer() {
  return (
    <footer className="mt-auto border-t border-ink-200/70 bg-ink-900 text-ink-200 dark:border-ink-800">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 md:grid-cols-3 md:px-6">
        <div>
          <p className="font-display text-2xl font-semibold text-white">WanderAI</p>
          <p className="mt-2 max-w-sm text-sm text-ink-400">
            Plan smarter journeys with AI itineraries, live weather, maps, and budget analytics —
            built as a premium travel SaaS experience.
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-300">Explore</p>
          <div className="mt-3 flex flex-col gap-2 text-sm">
            <Link to="/" className="hover:text-white">
              Home
            </Link>
            <Link to="/planner" className="hover:text-white">
              Trip Planner
            </Link>
            <Link to="/history" className="hover:text-white">
              Trip History
            </Link>
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-300">Contact</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <FiMail className="text-brand-400" /> hello@wanderai.app
            </li>
            <li className="flex items-center gap-2">
              <FiMapPin className="text-brand-400" /> Remote · Worldwide
            </li>
            <li className="flex items-center gap-2">
              <FiGithub className="text-brand-400" /> github.com/wanderai
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-ink-800 px-4 py-4 text-center text-xs text-ink-500">
        © {new Date().getFullYear()} WanderAI · AI Trip Planner Agent. All rights reserved.
      </div>
    </footer>
  )
}
