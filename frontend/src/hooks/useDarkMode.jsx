import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const DarkModeContext = createContext(null)

/**
 * Shared dark-mode provider — keeps <html class="dark"> in sync across the app.
 */
export function DarkModeProvider({ children }) {
  const [dark, setDark] = useState(() => {
    if (typeof window === 'undefined') return false
    const saved = localStorage.getItem('wanderai-theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    const root = document.documentElement
    if (dark) {
      root.classList.add('dark')
      localStorage.setItem('wanderai-theme', 'dark')
    } else {
      root.classList.remove('dark')
      localStorage.setItem('wanderai-theme', 'light')
    }
  }, [dark])

  const value = useMemo(
    () => ({
      dark,
      setDark,
      toggle: () => setDark((prev) => !prev),
    }),
    [dark],
  )

  return <DarkModeContext.Provider value={value}>{children}</DarkModeContext.Provider>
}

export function useDarkMode() {
  const ctx = useContext(DarkModeContext)
  if (!ctx) {
    throw new Error('useDarkMode must be used within DarkModeProvider')
  }
  return ctx
}
