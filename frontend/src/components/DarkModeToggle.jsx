import { FiMoon, FiSun } from 'react-icons/fi'
import { useDarkMode } from '../hooks/useDarkMode.jsx'

/**
 * Light / dark theme toggle button.
 */
export default function DarkModeToggle() {
  const { dark, toggle } = useDarkMode()

  return (
    <button
      type="button"
      onClick={toggle}
      className="rounded-xl border border-ink-200 bg-white/70 p-2.5 text-ink-700 transition hover:bg-white dark:border-ink-700 dark:bg-ink-900/70 dark:text-ink-200"
      aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {dark ? <FiSun size={16} /> : <FiMoon size={16} />}
    </button>
  )
}
