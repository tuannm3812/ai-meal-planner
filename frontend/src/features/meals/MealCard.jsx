import { Link } from 'react-router-dom'

import DishIllustration from '../../components/illustrations/DishIllustration'
import { MACROS } from '../plan/plan'

// One meal on Home, My meals and Past plans: its dish drawing, name, kcal and
// a Viridis macro bar with the split written out.
function MealCard({ meal }) {
  return (
    <Link
      className="flex flex-col gap-2.5 rounded-3xl bg-surface p-5 text-ink hover:ring-2 hover:ring-leaf focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
      to={`/plans/${encodeURIComponent(meal.requestId)}`}
    >
      <DishIllustration
        className="h-[120px] w-full rounded-2xl bg-tint"
        mealName={meal.name}
        type={meal.dish ?? undefined}
      />
      <span className="text-lg font-semibold">{meal.name ?? 'Untitled meal'}</span>
      {meal.kcal !== null && (
        <span className="font-display text-[28px] font-extrabold leading-none">{meal.kcal} kcal</span>
      )}
      {meal.split && (
        <>
          <span aria-hidden="true" className="flex h-2.5 overflow-hidden rounded-full">
            {MACROS.map((macro) => (
              <span className={macro.bar} key={macro.key} style={{ width: `${meal.split[macro.key]}%` }} />
            ))}
          </span>
          <span className="text-[13px] text-muted">
            {MACROS.map((macro) => `${macro.label} ${Math.round(meal.split[macro.key])}%`).join(' · ')}
          </span>
        </>
      )}
      {meal.craving && <span className="text-[13px] text-muted">For &ldquo;{meal.craving}&rdquo;</span>}
    </Link>
  )
}

export default MealCard
