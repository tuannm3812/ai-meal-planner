// A price tag (DESIGN.md §6): a label with a pointed end and a punched hole.
// It marks a plan's result or a number you would read off a shelf, always in
// words. `accent` is the deeper coral fill with white text (4.65:1).
const TONES = {
  good: 'bg-success-bg text-success-fg',
  warn: 'bg-estimate-bg text-estimate-fg',
  info: 'bg-surface text-ink',
  accent: 'bg-accent-fill text-white',
}

function PriceTag({ tone = 'info', children, className = '' }) {
  return (
    <span
      className={`inline-flex min-h-[32px] items-center gap-2 py-1 pl-5 pr-3.5 text-sm font-semibold [clip-path:polygon(12px_0,100%_0,100%_100%,12px_100%,0_50%)] ${TONES[tone]} ${className}`.trim()}
    >
      <span aria-hidden="true" className="-ml-1.5 h-1.5 w-1.5 shrink-0 rounded-full border border-current" />
      {children}
    </span>
  )
}

export default PriceTag
