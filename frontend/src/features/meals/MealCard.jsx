import { Link } from 'react-router-dom'

import DishIllustration from '../../components/illustrations/DishIllustration'
import MacroBar from '../plan/charts/MacroBar'

// One meal on Home, My meals and Past plans: its dish drawing, name, kcal and
// a Viridis macro bar with each share written inside it.
function MealCard({ meal }) {
  return (
    <Link
      className="flex flex-col gap-2.5 rounded-3xl bg-surface p-5 text-ink hover:ring-2 hover:ring-cobalt focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
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
      {meal.split && <MacroBar split={meal.split} />}
      {meal.craving && <span className="text-[13px] text-muted">For &ldquo;{meal.craving}&rdquo;</span>}
    </Link>
  )
}

export default MealCard
