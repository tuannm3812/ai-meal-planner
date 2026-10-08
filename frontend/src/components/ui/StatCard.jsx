function StatCard({ dot, label, value }) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
        <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{label}</p>
      </div>
      <p className="mt-3 text-2xl font-bold tracking-tight text-gray-900">{value}</p>
    </div>
  )
}

export default StatCard
