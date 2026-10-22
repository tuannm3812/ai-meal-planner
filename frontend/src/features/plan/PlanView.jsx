import {
  AMDR_PERCENT,
  MACROS,
  balanceOutcome,
  calories,
  estimatedCount,
  howItWasMade,
  inRange,
  ingredients,
  matchBadge,
  servedSplit,
} from './plan'

const TONES = {
  good: 'bg-success-bg text-success-fg',
  warn: 'bg-amber-100 text-amber-900',
  info: 'bg-ground text-ink border border-line',
}

function Badge({ tone = 'info', children }) {
  return (
    <span className={`rounded-full px-3 py-1 text-sm font-medium ${TONES[tone]}`}>{children}</span>
  )
}

const card = 'rounded-[20px] border border-line bg-surface p-6'
const heading = 'font-display text-xl font-bold text-ink'
const grams = (value) => `${Math.round(value)} g`

function BalanceBars({ split, outcome }) {
  return (
    <div className="mt-5 flex flex-col gap-5">
      {MACROS.map((macro) => {
        const [low, high] = AMDR_PERCENT[macro.key]
        const percent = split[macro.key]
        const inside = inRange(macro.key, percent)
        return (
          <div key={macro.key}>
            <div className="flex items-baseline justify-between gap-3 text-sm">
              <span className="font-medium text-ink">{macro.label}</span>
              <span className="text-muted">
                <strong className="text-base text-ink">{Math.round(percent)}%</strong> · range{' '}
                {low}–{high}%
                {!inside && <span className="ml-1 font-semibold text-amber-900">(outside)</span>}
              </span>
            </div>
            <div aria-hidden="true" className="relative mt-2 h-3 overflow-hidden rounded-full bg-ground">
              <div
                className="absolute inset-y-0 bg-line"
                data-testid={`band-${macro.key}`}
                style={{ left: `${low}%`, width: `${high - low}%` }}
              />
              <div
                className={`absolute inset-y-0 left-0 rounded-full ${inside ? macro.bar : 'bg-amber-600'}`}
                style={{ width: `${Math.min(percent, 100)}%`, opacity: 0.85 }}
              />
            </div>
          </div>
        )
      })}
      {outcome && (
        <p className="text-sm text-muted">
          The shaded band is the recommended range. The verdict above is the service&rsquo;s,
          not read from these bars.
        </p>
      )}
    </div>
  )
}

// docs/8_design.md §3.3: one response, top to bottom. plan_status, the
// balance outcome, the final nutrition and the warnings stay separate.
function PlanView({ plan, craving, onEditCraving }) {
  const match = matchBadge(plan)
  const outcome = balanceOutcome(plan)
  const estimated = estimatedCount(plan)
  const energy = calories(plan)
  const split = servedSplit(plan?.nutrition)
  const items = ingredients(plan)
  const notes = howItWasMade(plan)
  const mealName = plan?.meal_plan?.meal_definition?.structured_meal_name || 'Untitled meal'

  return (
    <>
      <section aria-labelledby="plan-heading" className={card}>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm text-muted">For your craving &ldquo;{craving}&rdquo;</p>
            <h2
              className="mt-1 font-display text-3xl font-bold tracking-tight text-ink"
              id="plan-heading"
            >
              {mealName}
            </h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {match && <Badge tone={match.tone}>{match.label}</Badge>}
              {outcome && <Badge tone={outcome.tone}>{outcome.label}</Badge>}
              {estimated && <Badge>Some nutrition estimated</Badge>}
            </div>
          </div>
          {onEditCraving && (
            <button
              className="min-h-[44px] shrink-0 rounded-xl border border-ink px-4 text-sm font-semibold text-ink hover:bg-ground focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
              onClick={onEditCraving}
              type="button"
            >
              Try another craving
            </button>
          )}
        </div>

        {plan?.plan_status === 'fallback' && (
          <p className="mt-4 rounded-[14px] border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Nothing on the menu is a close match for &ldquo;{craving}&rdquo;, so this is a
            standard meal instead.
          </p>
        )}

        {estimated && (
          <p className="mt-4 text-sm text-muted">
            {estimated.estimated} of {estimated.of} ingredients use estimated nutrition from local
            tables, so these numbers are approximate.
            {outcome && ' “On target” is measured against those same tables, so it is not an independent check.'}
          </p>
        )}
      </section>

      {energy && (
        <section aria-label="Calories" className={`${card} grid grid-cols-3 gap-4 sm:grid-cols-4`}>
          <div className="col-span-3 sm:col-span-1">
            <p className="text-sm text-muted">This meal</p>
            <p className="font-display text-3xl font-bold text-ink">
              {Math.round(energy.total)} kcal
            </p>
            {energy.target !== null && (
              <p className="text-sm text-muted">Meal target: {energy.target} kcal</p>
            )}
          </div>
          {MACROS.map(
            (macro) =>
              energy.grams[macro.key] !== null && (
                <div key={macro.key}>
                  <p className="text-sm text-muted">{macro.label}</p>
                  <p className="text-2xl font-semibold text-ink">{grams(energy.grams[macro.key])}</p>
                </div>
              ),
          )}
        </section>
      )}

      {(split || outcome) && (
        <section aria-labelledby="balance-heading" className={card}>
          <h3 className={heading} id="balance-heading">
            Balance
          </h3>
          {outcome && (
            <div className="mt-2">
              <p className="text-sm text-muted">{outcome.body}</p>
              {plan?.reconciliation?.rescaled && (
                <p className="mt-1 text-sm text-muted">
                  All portions were then scaled toward the meal&rsquo;s calorie target.
                </p>
              )}
            </div>
          )}
          {split ? (
            <BalanceBars outcome={outcome} split={split} />
          ) : (
            <p className="mt-3 text-sm text-muted">This response has no nutrition to split.</p>
          )}
        </section>
      )}

      {items.length > 0 && (
        <section aria-labelledby="ingredients-heading" className={card}>
          <h3 className={heading} id="ingredients-heading">
            Ingredients
          </h3>
          <ul className="mt-4 divide-y divide-line">
            {items.map((item) => (
              <li className="flex items-center justify-between gap-4 py-3" key={item.name}>
                <span className="flex flex-wrap items-center gap-2 text-ink">
                  {item.name}
                  {item.tag && (
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        item.estimated ? 'bg-amber-100 text-amber-900' : 'bg-success-bg text-success-fg'
                      }`}
                    >
                      {item.tag}
                    </span>
                  )}
                </span>
                {typeof item.grams === 'number' && (
                  <span className="shrink-0 text-muted">{item.grams} g</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {notes.length > 0 && (
        <details className={card}>
          <summary className="cursor-pointer font-semibold text-ink">How this plan was made</summary>
          <ul className="mt-3 list-disc space-y-1.5 pl-5 text-sm text-muted">
            {notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </details>
      )}
    </>
  )
}

export default PlanView
