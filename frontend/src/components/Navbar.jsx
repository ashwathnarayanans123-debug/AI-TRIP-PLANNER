import { Link, NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineMenuAlt3, HiOutlineX } from 'react-icons/hi'
import { useState } from 'react'
import DarkModeToggle from './DarkModeToggle'

const links = [
  { to: '/', label: 'Home' },
  { to: '/planner', label: 'Plan Trip' },
  { to: '/history', label: 'My Trips' },
]

/**
 * Top navigation with glassmorphism and mobile drawer.
 */
export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-white/20 bg-white/60 backdrop-blur-xl dark:border-ink-800/80 dark:bg-ink-950/70">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 md:px-6">
        <Link to="/" className="group flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-sm font-bold text-white shadow-md shadow-brand-600/30">
            W
          </span>
          <div>
            <p className="font-display text-xl font-semibold leading-none text-ink-900 dark:text-white">
              WanderAI
            </p>
            <p className="text-[10px] uppercase tracking-[0.18em] text-brand-700 dark:text-brand-300">
              Trip Planner
            </p>
          </div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-xl px-3.5 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-brand-500/15 text-brand-800 dark:text-brand-200'
                    : 'text-ink-600 hover:bg-ink-100/80 dark:text-ink-300 dark:hover:bg-ink-800'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <DarkModeToggle />
          <Link to="/planner" className="btn-primary ml-2">
            Start Planning
          </Link>
        </nav>

        <div className="flex items-center gap-2 md:hidden">
          <DarkModeToggle />
          <button
            type="button"
            className="rounded-xl border border-ink-200 p-2 dark:border-ink-700"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {open ? <HiOutlineX size={20} /> : <HiOutlineMenuAlt3 size={20} />}
          </button>
        </div>
      </div>

      {open && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t border-ink-200/60 px-4 py-3 md:hidden dark:border-ink-800"
        >
          <div className="flex flex-col gap-1">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setOpen(false)}
                className="rounded-xl px-3 py-2.5 text-sm font-medium text-ink-700 dark:text-ink-200"
              >
                {link.label}
              </NavLink>
            ))}
            <Link to="/planner" onClick={() => setOpen(false)} className="btn-primary mt-2">
              Start Planning
            </Link>
          </div>
        </motion.div>
      )}
    </header>
  )
}
