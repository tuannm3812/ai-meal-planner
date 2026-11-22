import { AMDR_PERCENT, MACROS, inRange } from '../plan'

// Each macro's share on a track, over a green band for its recommended range.
// The verdict is the service's, never read from these bars.
function RangeBars({ split }) {
  return (
    <div className="flex flex-col gap-4">
      {MACROS.map((macro) => {
        const [low, high] = AMDR_PERCENT[macro.key]
        const percent = split[macro.key]
        const inside = inRange(macro.key, percent)
        return (
          <div key={macro.key}>
            <div className="flex items-baseline justify-between gap-3 text-sm">
              <span className="font-semibold text-ink">{macro.label}</span>
              <span className="text-muted">
                <strong className="text-base text-ink">{Math.round(percent)}%</strong> · range{' '}
                {low}–{high}%
                {!inside && <span className="ml-1 font-semibold text-estimate-fg">(outside)</span>}
              </span>
            </div>
            <div aria-hidden="true" className="relative mt-1.5 h-3.5 rounded-full bg-ground">
              <div
                className="absolute inset-y-0 rounded-full bg-band"
                data-testid={`band-${macro.key}`}
                style={{ left: `${low}%`, width: `${high - low}%` }}
              />
              <div
                className={`absolute inset-y-[3px] left-0 rounded-full ${inside ? macro.bar : 'bg-estimate-fg'}`}
                style={{ width: `${Math.min(percent, 100)}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default RangeBars
