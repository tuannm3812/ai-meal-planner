import { MACROS } from '../plan'
import { MACRO_COLORS, donutSegments } from './geometry'

const R = 48

// The served split as a donut, with grams and shares written beside it, so
// colour is never the only way to read it.
function MacroDonut({ split, grams }) {
  const segments = donutSegments(split, R)
  const label = MACROS.map((macro) => `${macro.label} ${Math.round(split[macro.key])}%`).join(', ')
  return (
    <figure className="m-0 flex items-center gap-5">
      <svg aria-label={`${label} of calories`} className="h-[150px] w-[150px] shrink-0" role="img" viewBox="0 0 140 140">
        {segments.map((segment) => (
          <circle
            cx="70"
            cy="70"
            fill="none"
            key={segment.key}
            r={R}
            stroke={MACRO_COLORS[segment.key]}
            strokeDasharray={`${segment.length} ${segment.circumference - segment.length}`}
            strokeDashoffset={segment.offset}
            strokeWidth="22"
            transform="rotate(-90 70 70)"
          />
        ))}
      </svg>
      <figcaption className="flex flex-col gap-2 text-[15px] text-ink">
        {MACROS.map((macro) => (
          <span className="flex items-center gap-2 whitespace-nowrap" key={macro.key}>
            <span aria-hidden="true" className={`h-3 w-3 shrink-0 rounded ${macro.bar}`} />
            {grams?.[macro.key] !== null && grams?.[macro.key] !== undefined && (
              <strong className="whitespace-nowrap font-display text-[22px] font-extrabold">
                {Math.round(grams[macro.key])} g
              </strong>
            )}
            <span>
              {macro.label.toLowerCase()} · {Math.round(split[macro.key])}%
            </span>
          </span>
        ))}
      </figcaption>
    </figure>
  )
}

export default MacroDonut
