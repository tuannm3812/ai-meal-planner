import SectionCard from '../../components/ui/SectionCard'

// The service decides whether a plan meets the targets (DEC-25, DEC-26); the
// dashboard only reports its `macro_balance` record, so the ranges live in
// one place.
const OUTCOMES = {
  in_range: {
    label: 'On target',
    body: 'Calories and the protein, carb and fat split are inside the recommended ranges.',
    tone: 'bg-emerald-50 text-emerald-700',
  },
  rebalanced: {
    label: 'Portions rebalanced',
    body: 'Ingredient portions were resized so the meal fits the recommended ranges.',
    tone: 'bg-emerald-50 text-emerald-700',
  },
  no_feasible_balance: {
    label: 'Outside the ranges',
    body: "This meal's ingredients cannot be resized into the recommended ranges.",
    tone: 'bg-amber-50 text-amber-700',
  },
  reverted: {
    label: 'Outside the ranges',
    body: 'Resized portions missed the ranges once checked, so the original portions are shown.',
    tone: 'bg-amber-50 text-amber-700',
  },
}

const SPLIT = [
  { key: 'protein', label: 'Protein', dot: 'bg-sky-500' },
  { key: 'carbs', label: 'Carbs', dot: 'bg-violet-500' },
  { key: 'fat', label: 'Fat', dot: 'bg-rose-500' },
]

function MealQuality({ craving, planStatus, macroBalance, warnings }) {
  const outcome = macroBalance && OUTCOMES[macroBalance.outcome]
  const split =
    macroBalance?.outcome === 'rebalanced'
      ? macroBalance.macro_percent_after
      : macroBalance?.macro_percent_before

  if (planStatus !== 'fallback' && !outcome && !warnings.length) return null

  return (
    <SectionCard eyebrow="Quality" title="Meal Quality">
      {planStatus === 'fallback' && (
        <p className="mb-5 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Nothing on the menu is a close match for &ldquo;{craving}&rdquo;, so this is a
          standard meal instead.
        </p>
      )}

      {outcome && (
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${outcome.tone}`}>
              {outcome.label}
            </span>
            <p className="mt-2 text-sm text-gray-500">{outcome.body}</p>
            <p className="mt-1 text-xs text-gray-400">
              Meal target: {macroBalance.target_meal_calories} kcal
            </p>
          </div>
          {split && (
            <dl className="flex gap-5" aria-label="Share of calories">
              {SPLIT.map((macro) => (
                <div key={macro.key}>
                  <dt className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500">
                    <span className={`h-2 w-2 rounded-full ${macro.dot}`} />
                    {macro.label}
                  </dt>
                  <dd className="mt-1 text-lg font-bold text-gray-900">
                    {Math.round(split[macro.key])}%
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      )}

      {warnings.length > 0 && (
        <ul className="mt-5 list-disc space-y-1 pl-5 text-sm text-gray-500">
          {warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
    </SectionCard>
  )
}

export default MealQuality
