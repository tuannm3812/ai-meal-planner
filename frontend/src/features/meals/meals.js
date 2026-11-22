import { dishType } from '../../components/illustrations/dishType'
import { servedSplit } from '../plan/plan'

const newestFirst = (items) =>
  [...(items || [])].sort((a, b) => String(b?.saved_at ?? '').localeCompare(String(a?.saved_at ?? '')))

// Feedback is append-only on the server (spec §4.4), so one plan can have
// several saved records. Keep the newest per plan.
export function dedupeSaved(items) {
  const seen = new Set()
  const meals = []
  for (const item of newestFirst(items)) {
    if (!item?.saved || !item.request_id || seen.has(item.request_id)) continue
    seen.add(item.request_id)
    meals.push(item)
  }
  return meals
}

// A stored plan from GET /meal-plans by its request ID, or null.
export function findPlan(items, requestId) {
  return (items || []).find((item) => item?.request_id === requestId) ?? null
}

// What a card shows for a stored plan. Missing numbers stay null.
export function planSummary(plan) {
  const name = plan?.meal_plan?.meal_definition?.structured_meal_name ?? null
  const kcal = plan?.nutrition?.total_calories
  return {
    requestId: plan?.request_id ?? null,
    name,
    craving: plan?.request?.craving ?? null,
    kcal: typeof kcal === 'number' ? Math.round(kcal) : null,
    split: servedSplit(plan?.nutrition),
    dish: dishType(name),
    status: plan?.plan_status ?? null,
  }
}

// History holds every plan, infeasible ones included; cards show meals only.
export function pastMeals(items) {
  return newestFirst(items)
    .filter((item) => item?.plan_status !== 'infeasible' && item?.meal_plan)
    .map(planSummary)
}
