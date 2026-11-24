import { AMDR_PERCENT, MACROS, inRange } from '../plan'

// Three readings side by side: each macro's share of the calories, with a
// scale that shades its recommended range and marks where the meal sits.
// The verdict is the service's, never read from these scales.
function RangeBars({ split, grams = null }) {
  return (
    <div className="grid gap-y-5 md:grid-cols-3 md:divide-x md:divide-line">
      {MACROS.map((macro) => {
        const [low, high] = AMDR_PERCENT[macro.key]
        const percent = split[macro.key]
        const inside = inRange(macro.key, percent)
        return (
          <div className="md:px-5 md:first:pl-0 md:last:pr-0" key={macro.key}>
            <p className="flex items-center gap-2 text-sm font-semibold text-ink">
              <span aria-hidden="true" className={`h-3 w-3 rounded ${macro.bar}`} />
              {macro.label}
              {typeof grams?.[macro.key] === 'number' && (
                <span className="ml-auto font-mono font-bold text-ink">{Math.round(grams[macro.key])} g</span>
              )}
            </p>
            <p className="mt-1 flex flex-wrap items-baseline gap-x-2">
              <strong className="font-display text-[30px] font-extrabold leading-none text-ink">
                {Math.round(percent)}%
              </strong>
              {!inside && <span className="text-sm font-semibold text-estimate-fg">(outside)</span>}
            </p>
            <div aria-hidden="true" className="relative mt-3 h-2.5 rounded-full bg-ground">
              <div
                className="absolute inset-y-0 rounded-full bg-band"
                data-testid={`band-${macro.key}`}
                style={{ left: `${low}%`, width: `${high - low}%` }}
              />
              <div
                className={`absolute top-1/2 h-5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-surface ${inside ? macro.bar : 'bg-estimate-fg'}`}
                style={{ left: `${Math.min(percent, 100)}%` }}
              />
            </div>
            <p className="mt-2 text-sm text-muted">
              range {low}–{high}%
            </p>
          </div>
        )
      })}
    </div>
  )
}

export default RangeBars
