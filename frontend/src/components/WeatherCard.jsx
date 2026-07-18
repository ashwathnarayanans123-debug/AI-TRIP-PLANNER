import { FiCloud, FiDroplet, FiWind, FiThermometer } from 'react-icons/fi'

/**
 * Current weather + 5-day forecast cards.
 */
export default function WeatherCard({ weather, loading }) {
  if (loading) {
    return (
      <div className="glass space-y-3 p-5">
        <div className="skeleton h-6 w-40" />
        <div className="skeleton h-20 w-full" />
        <div className="grid grid-cols-5 gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skeleton h-24" />
          ))}
        </div>
      </div>
    )
  }

  if (!weather) {
    return (
      <div className="glass p-5 text-sm text-ink-500">
        Weather will appear here once a destination is planned.
      </div>
    )
  }

  const { current, forecast, city, country } = weather

  return (
    <section className="glass p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-xl font-semibold text-ink-900 dark:text-white">
            Weather in {city}
            {country ? `, ${country}` : ''}
          </h3>
          <p className="mt-1 text-sm capitalize text-ink-500">{current.description}</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-semibold text-brand-700 dark:text-brand-300">
            {Math.round(current.temperature)}°C
          </p>
          <p className="text-xs text-ink-500">{current.weather}</p>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat icon={FiThermometer} label="Range" value={`${Math.round(current.temp_min)}–${Math.round(current.temp_max)}°`} />
        <Stat icon={FiDroplet} label="Humidity" value={`${Math.round(current.humidity)}%`} />
        <Stat icon={FiWind} label="Wind" value={`${current.wind.toFixed(1)} m/s`} />
        <Stat icon={FiCloud} label="Rain chance" value={`${Math.round(current.rain_chance)}%`} />
      </div>

      {forecast?.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-500">
            5-day forecast
          </p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
            {forecast.map((day) => (
              <div
                key={day.date}
                className="rounded-xl border border-ink-200/70 bg-white/50 p-3 text-center dark:border-ink-700 dark:bg-ink-900/50"
              >
                <p className="text-[11px] font-medium text-ink-500">{day.date}</p>
                <p className="mt-1 text-lg font-semibold text-ink-900 dark:text-white">
                  {Math.round(day.temperature)}°
                </p>
                <p className="text-[11px] text-ink-500">{day.weather}</p>
                <p className="text-[10px] text-ink-400">Rain {Math.round(day.rain_chance)}%</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="rounded-xl border border-ink-200/60 bg-white/40 px-3 py-2 dark:border-ink-700 dark:bg-ink-900/40">
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wide text-ink-500">
        <Icon /> {label}
      </div>
      <p className="mt-1 text-sm font-semibold text-ink-800 dark:text-ink-100">{value}</p>
    </div>
  )
}
