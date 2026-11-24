import { dishType } from '../../components/illustrations/dishType'
import { balanceOutcome, mealTarget, servedSplit } from '../plan/plan'

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
    // When it was made, for the dated list; null when the record says nothing.
    date: plan?.saved_at ?? plan?.generated_at ?? null,
    target: typeof mealTarget(plan) === 'number' ? Math.round(mealTarget(plan)) : null,
    outcome: balanceOutcome(plan),
  }
}

// History holds every plan, infeasible ones included; cards show meals only.
export function pastMeals(items) {
  return newestFirst(items)
    .filter((item) => item?.plan_status !== 'infeasible' && item?.meal_plan)
    .map(planSummary)
}

const dayKey = (date) => `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`

// Meals grouped by the day they were made, in the order given (newest first).
// "Today" and "Yesterday" are by this device's clock; undated plans go last.
export function byDay(meals, now = new Date()) {
  const today = dayKey(now)
  const yesterday = dayKey(new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1))
  const groups = new Map()
  for (const meal of meals) {
    const parsed = meal.date ? new Date(meal.date) : null
    const valid = parsed && !Number.isNaN(parsed.getTime())
    const key = valid ? dayKey(parsed) : 'undated'
    if (!groups.has(key)) {
      let label = 'Earlier'
      if (key === today) label = 'Today'
      else if (key === yesterday) label = 'Yesterday'
      else if (valid) {
        label = parsed.toLocaleDateString('en-AU', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
      }
      groups.set(key, { key, label, meals: [] })
    }
    groups.get(key).meals.push(meal)
  }
  return [...groups.values()]
}

// The meals whose name or craving holds every word typed.
export function searchMeals(meals, query) {
  const words = String(query ?? '').toLowerCase().split(/\s+/).filter(Boolean)
  if (!words.length) return meals
  return meals.filter((meal) => {
    const text = `${meal.name ?? ''} ${meal.craving ?? ''}`.toLowerCase()
    return words.every((word) => text.includes(word))
  })
}
