import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'

const COLORS = ['#0d9488', '#0284c7', '#d97706', '#7c3aed', '#db2777', '#64748b']

/**
 * Budget analytics charts (pie + bar) for accommodation, food, transport, etc.
 */
export default function BudgetChart({ breakdown, total, currency = 'INR' }) {
  if (!breakdown) {
    return (
      <div className="glass p-5 text-sm text-ink-500">
        Budget charts appear after a plan is generated.
      </div>
    )
  }

  const data = [
    { name: 'Accommodation', value: Number(breakdown.accommodation || 0) },
    { name: 'Food', value: Number(breakdown.food || 0) },
    { name: 'Transportation', value: Number(breakdown.transportation || 0) },
    { name: 'Tickets', value: Number(breakdown.tickets || 0) },
    { name: 'Shopping', value: Number(breakdown.shopping || 0) },
    { name: 'Miscellaneous', value: Number(breakdown.miscellaneous || 0) },
  ].filter((d) => d.value > 0)

  if (data.length === 0) {
    return (
      <div className="glass p-5 text-sm text-ink-500">No budget breakdown available.</div>
    )
  }

  return (
    <section className="glass p-5">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <div>
          <h3 className="font-display text-xl font-semibold text-ink-900 dark:text-white">
            Budget Analytics
          </h3>
          <p className="text-sm text-ink-500">Where your trip spend goes</p>
        </div>
        {total != null && (
          <p className="text-lg font-semibold text-brand-700 dark:text-brand-300">
            {currency} {Number(total).toLocaleString()}
          </p>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={3}
              >
                {data.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => [`${currency} ${Number(v).toFixed(0)}`, 'Amount']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#94a3b833" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => [`${currency} ${Number(v).toFixed(0)}`, 'Amount']} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}
