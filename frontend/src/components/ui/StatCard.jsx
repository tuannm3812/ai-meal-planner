function StatCard({ dot, label, value }) {
  return (
    <div className="rounded-xl border border-transparent bg-white p-5">
      <div className="flex items-center gap-2">
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
        <p className="text-xs font-semibold uppercase tracking-wider text-muted">{label}</p>
      </div>
      <p className="mt-3 text-2xl font-bold tracking-tight text-ink">{value}</p>
    </div>
  )
}

export default StatCard
