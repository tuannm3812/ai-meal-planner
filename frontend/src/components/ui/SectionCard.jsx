function SectionCard({ eyebrow, title, children, className = '' }) {
  return (
    <section className={`rounded-3xl border border-transparent bg-white p-6 ${className}`}>
      <div>
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-wider text-carbs">
            {eyebrow}
          </p>
        )}
        <h2 className="mt-1 text-lg font-semibold text-ink">{title}</h2>
      </div>
      <div className="mt-5">{children}</div>
    </section>
  )
}

export default SectionCard
