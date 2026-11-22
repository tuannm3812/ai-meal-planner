function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-transparent bg-surface p-5">
      <p className="text-xs font-semibold uppercase tracking-wider text-muted">{label}</p>
      <p className="mt-3 text-2xl font-bold tracking-tight text-ink">{value}</p>
    </div>
  )
}

export default StatCard
