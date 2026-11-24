import { MACROS } from '../plan'

// The served split as one bar with each share written inside its segment,
// over a key naming the colours. A segment too thin for its number leaves it
// out; the sentence for screen readers always has all three.
function MacroBar({ split }) {
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
      <span aria-hidden="true" className="flex flex-wrap gap-x-3 gap-y-1 text-[13px] text-muted">
        {shares.map((macro) => (
          <span className="flex items-center gap-1.5" key={macro.key}>
            <span className={`h-2.5 w-2.5 rounded-sm ${macro.bar}`} />
            {macro.label}
          </span>
        ))}
      </span>
    </span>
  )
}

export default MacroBar
