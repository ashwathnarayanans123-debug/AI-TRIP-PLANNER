import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { IoClose, IoCheckmarkCircle, IoWarning, IoInformationCircle } from 'react-icons/io5'

const ToastContext = createContext(null)

const ICONS = {
  success: IoCheckmarkCircle,
  error: IoWarning,
  info: IoInformationCircle,
}

const STYLES = {
  success: 'border-brand-400/40 bg-brand-50 text-brand-900 dark:bg-brand-950 dark:text-brand-100',
  error: 'border-red-400/40 bg-red-50 text-red-900 dark:bg-red-950 dark:text-red-100',
  info: 'border-sky-400/40 bg-sky-50 text-sky-900 dark:bg-sky-950 dark:text-sky-100',
}

/**
 * Global toast notification provider + hook.
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const push = useCallback(
    (message, type = 'info', duration = 3500) => {
      const id = crypto.randomUUID()
      setToasts((prev) => [...prev, { id, message, type }])
      window.setTimeout(() => dismiss(id), duration)
    },
    [dismiss],
  )

  const value = useMemo(
    () => ({
      toast: push,
      success: (msg) => push(msg, 'success'),
      error: (msg) => push(msg, 'error'),
      info: (msg) => push(msg, 'info'),
    }),
    [push],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[min(100%,22rem)] flex-col gap-2">
        <AnimatePresence>
          {toasts.map((t) => {
            const Icon = ICONS[t.type] || IoInformationCircle
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, y: 16, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.96 }}
                className={`pointer-events-auto flex items-start gap-3 rounded-2xl border px-4 py-3 shadow-glass ${STYLES[t.type]}`}
              >
                <Icon className="mt-0.5 shrink-0 text-lg" />
                <p className="flex-1 text-sm font-medium">{t.message}</p>
                <button
                  type="button"
                  onClick={() => dismiss(t.id)}
                  className="rounded-lg p-1 opacity-70 transition hover:opacity-100"
                  aria-label="Dismiss"
                >
                  <IoClose />
                </button>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return ctx
}
