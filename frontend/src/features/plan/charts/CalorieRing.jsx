import { neutral, VIRIDIS } from '../../../theme/tokens'
import { ringFraction } from './geometry'

const R = 56
const CIRCUMFERENCE = 2 * Math.PI * R

// This meal's kcal against its target. The text gives both numbers; the arc
// only shows how full the target is.
function CalorieRing({ total, target }) {
  const fraction = ringFraction(total, target)
  const served = Math.round(total)
  const label =
    target === null
      ? `${served} kcal`
      : `${served} kcal against a ${Math.round(target)} kcal meal target`
  return (
    <figure className="m-0 flex items-center gap-4">
      <svg aria-label={label} className="h-[150px] w-[150px] shrink-0" role="img" viewBox="0 0 140 140">
        <circle cx="70" cy="70" fill="none" r={R} stroke={neutral.tint} strokeWidth="14" />
        {fraction !== null && (
          <circle
            cx="70"
            cy="70"
            fill="none"
            r={R}
            stroke={VIRIDIS[1]}
            strokeDasharray={`${fraction * CIRCUMFERENCE} ${CIRCUMFERENCE}`}
            strokeLinecap={fraction < 1 ? 'round' : 'butt'}
            strokeWidth="14"
            transform="rotate(-90 70 70)"
          />
        )}
        <text
          className="fill-ink font-display text-[32px] font-extrabold"
          textAnchor="middle"
          x="70"
          y={target === null ? 80 : 72}
        >
          {served}
        </text>
        <text className="fill-muted text-[13px] font-medium" textAnchor="middle" x="70" y="94">
          {target === null ? 'kcal' : `of ${Math.round(target)} kcal`}
        </text>
      </svg>
      <figcaption className="max-w-[140px] text-sm text-muted">
        {target === null ? 'This meal' : 'This meal against its target'}
      </figcaption>
    </figure>
  )
}

export default CalorieRing
