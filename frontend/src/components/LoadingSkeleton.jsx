/**
 * Loading skeleton placeholders used while AI / API calls are in flight.
 */
export default function LoadingSkeleton({ variant = 'plan' }) {
  if (variant === 'cards') {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="glass space-y-3 p-5">
            <div className="skeleton h-3 w-24" />
            <div className="skeleton h-6 w-3/4" />
            <div className="skeleton h-4 w-1/2" />
            <div className="skeleton h-20 w-full" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="glass space-y-3 p-6">
        <div className="skeleton h-7 w-48" />
        <div className="skeleton h-4 w-full" />
        <div className="skeleton h-4 w-5/6" />
        <div className="skeleton h-4 w-2/3" />
      </div>
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="glass space-y-3 p-6">
          <div className="skeleton h-6 w-40" />
          <div className="grid gap-3 md:grid-cols-3">
            <div className="skeleton h-28" />
            <div className="skeleton h-28" />
            <div className="skeleton h-28" />
          </div>
        </div>
      ))}
    </div>
  )
}
