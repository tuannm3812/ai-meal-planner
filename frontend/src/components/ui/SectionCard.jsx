function SectionCard({ eyebrow, title, children, className = '' }) {
  return (
    <section className={`rounded-2xl border border-gray-100 bg-white p-6 shadow-sm ${className}`}>
      <div>
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
            {eyebrow}
          </p>
        )}
        <h2 className="mt-1 text-lg font-semibold text-gray-900">{title}</h2>
      </div>
      <div className="mt-5">{children}</div>
    </section>
  )
}

export default SectionCard
