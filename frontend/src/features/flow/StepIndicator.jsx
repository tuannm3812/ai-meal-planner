const STEPS = [
  { id: 'profile', number: 1, label: 'You' },
  { id: 'craving', number: 2, label: 'Craving' },
  { id: 'plan', number: 3, label: 'Your plan' },
]

// "1 · You, 2 · Craving, 3 · Your plan". A step can be opened once the steps
// before it allow it; the current one is marked for assistive technology.
function StepIndicator({ current, reachable, onGo }) {
  return (
    <nav aria-label="Progress">
      <ol className="flex flex-wrap gap-2 text-sm">
        {STEPS.map((step) => {
          const isCurrent = step.id === current
          const style = isCurrent
            ? 'bg-ink text-white font-semibold'
            : 'border border-line bg-surface text-muted hover:text-ink'
          return (
            <li key={step.id}>
              <button
                aria-current={isCurrent ? 'step' : undefined}
                className={`min-h-[44px] rounded-full px-4 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink disabled:cursor-not-allowed disabled:opacity-60 ${style}`}
                disabled={!isCurrent && !reachable[step.id]}
                onClick={() => onGo(step.id)}
                type="button"
              >
                {step.number} · {step.label}
              </button>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

export default StepIndicator
