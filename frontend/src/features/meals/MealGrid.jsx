import { HOSTED_FEEDBACK_MESSAGE } from '../plan/feedback'
import MealCard from './MealCard'
import PlanRows from './PlanRows'

// A list of meal cards (or dated rows) with its loading, empty, hosted and
// error states.
function MealGrid({ lists, meals, empty, max, rows = false }) {
  if (lists.status === 'loading' || lists.status === 'idle') {
    return <p className="text-sm text-muted">Loading…</p>
  }
  if (lists.status === 'hosted') {
    return <p className="rounded-2xl bg-surface p-4 text-sm text-muted">{HOSTED_FEEDBACK_MESSAGE}</p>
  }
  if (lists.status === 'error') {
    return (
      <p className="rounded-2xl bg-surface p-4 text-sm text-accent-text" role="alert">
        {lists.error}
      </p>
    )
  }
  const shown = max ? meals.slice(0, max) : meals
  if (!shown.length) return <p className="rounded-2xl bg-surface p-4 text-sm text-muted">{empty}</p>
  if (rows) return <PlanRows meals={shown} />
  return (
    <ul className="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-5">
      {shown.map((meal) => (
        <li className="flex" key={meal.requestId}>
          <div className="w-full [&>a]:h-full">
            <MealCard meal={meal} />
          </div>
        </li>
      ))}
    </ul>
  )
}

export default MealGrid
