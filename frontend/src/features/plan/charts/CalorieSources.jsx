import { sourceSegments } from './geometry'

const TAG_STYLES = {
  Estimated: 'bg-estimate-bg text-estimate-fg',
  Reference: 'bg-success-bg text-success-fg',
  Verified: 'bg-success-bg text-success-fg',
}

// "Where the calories come from": one stacked bar, then each ingredient with
// its colour key, source tag, served grams and kcal. Ingredients without kcal
// are listed after the bar's, so nothing served goes missing.
function CalorieSources({ items }) {
  const segments = sourceSegments(items)
  const withoutKcal = items.filter((item) => !segments.some((segment) => segment.name === item.name))
  const rows = [...segments, ...withoutKcal]
  return (
    <div>
      {segments.length > 0 && (
        <div aria-hidden="true" className="flex h-[22px] gap-0.5 overflow-hidden rounded-lg">
          {segments.map((segment) => (
            <span
              key={segment.name}
              style={{ background: segment.color, flex: `${segment.kcal} 1 0`, minWidth: '4px' }}
            />
          ))}
        </div>
      )}
      <ul className="mt-3 divide-y divide-tint">
        {rows.map((item) => (
          <li className="flex items-center gap-3 py-3" key={item.name}>
            <span
              aria-hidden="true"
              className="h-3.5 w-3.5 shrink-0 rounded"
              style={{ background: item.color ?? 'transparent' }}
            />
            <span className="flex min-w-0 flex-1 flex-wrap items-center gap-2 text-ink">
              {item.name}
              {item.tag && (
                <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${TAG_STYLES[item.tag]}`}>
                  {item.tag}
                </span>
              )}
            </span>
            {typeof item.grams === 'number' && (
              <span className="w-16 shrink-0 text-right text-muted">{item.grams} g</span>
            )}
            {typeof item.kcal === 'number' && (
              <span className="w-20 shrink-0 text-right font-semibold text-ink">
                {Math.round(item.kcal)} kcal
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default CalorieSources
