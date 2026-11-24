import { MACROS } from '../plan'

// Which colour is which macro. Shown once for a list of bars, not on each bar.
export function MacroKey({ className = '' }) {
  return (
    <p aria-hidden="true" className={`flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-muted ${className}`.trim()}>
      {MACROS.map((macro) => (
        <span className="flex items-center gap-1.5" key={macro.key}>
          <span className={`h-2.5 w-2.5 rounded-sm ${macro.bar}`} />
          {macro.label}
        </span>
      ))}
    </p>
  )
}

// The served split as one bar with each share written inside its segment. A
// segment too thin for its number leaves it out; the sentence for screen
// readers always has all three. `withKey` adds the colour key under a bar that
// stands alone.
function MacroBar({ split, withKey = false }) {
  const shares = MACROS.map((macro) => ({ ...macro, percent: Math.round(split[macro.key]) }))
  return (
    <span className="flex flex-col gap-1.5">
      <span className="sr-only">
        {shares.map((macro) => `${macro.label} ${macro.percent}%`).join(' · ')}
      </span>
      <span aria-hidden="true" className="flex h-7 gap-0.5 overflow-hidden rounded-lg font-mono text-xs font-bold">
        {shares.map((macro) => (
          <span
            className={`flex items-center justify-center overflow-hidden ${macro.bar} ${macro.on}`}
            key={macro.key}
            style={{ width: `${split[macro.key]}%` }}
          >
            {macro.percent >= 12 && `${macro.percent}%`}
          </span>
        ))}
      </span>
      {withKey && <MacroKey />}
    </span>
  )
}

export default MacroBar
