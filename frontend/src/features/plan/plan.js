// What the plan screen (docs/8_design.md §3.3) reads from a MealPlanResponse.
// Every helper returns null when the response lacks what it needs, so the
// section that uses it is left out rather than filled with an invented value.

// Adult AMDR, % of energy. The service decides whether a plan meets these
// (DEC-25); the screen only draws them as the shaded band. plan.test.js reads
// backend/app/core/macro_balance.py so the two cannot drift apart.
export const AMDR_PERCENT = { protein: [10, 35], carbs: [45, 65], fat: [20, 35] }

const KCAL_PER_GRAM = { protein: 4, carbs: 4, fat: 9 }

export const MACROS = [
  { key: 'protein', label: 'Protein', total: 'total_protein', bar: 'bg-protein' },
  { key: 'carbs', label: 'Carbs', total: 'total_carbs', bar: 'bg-carbs' },
  { key: 'fat', label: 'Fat', total: 'total_fat', bar: 'bg-fat' },
]

const isNumber = (value) => typeof value === 'number' && Number.isFinite(value)

// The balance stage's verdict. It is the service's, never derived from the
// bars: calories can miss their target while every bar sits in range.
export const BALANCE_OUTCOMES = {
  in_range: {
    label: 'On target',
    body: 'Calories and the protein, carb and fat split are inside the recommended ranges.',
    tone: 'good',
  },
  rebalanced: {
    label: 'Portions rebalanced',
    body: 'Ingredient portions were resized so the meal fits the recommended ranges.',
    tone: 'good',
  },
  no_feasible_balance: {
    label: 'Outside the ranges',
    body: "This meal's ingredients could not be resized into the recommended ranges.",
    tone: 'warn',
  },
  reverted: {
    label: 'Outside the ranges',
    body: 'Resized portions missed the ranges once checked, so they were not used.',
    tone: 'warn',
  },
}

export function balanceOutcome(plan) {
  return BALANCE_OUTCOMES[plan?.macro_balance?.outcome] ?? null
}

// Each macro's share of the calories the three macros supply, from the
// served nutrition (as the service's macro_percentages computes it). The
// balance record describes an earlier stage that a rescale can follow.
export function servedSplit(nutrition) {
  if (!nutrition || !MACROS.every((macro) => isNumber(nutrition[macro.total]))) return null
  const energy = Object.fromEntries(
    MACROS.map((macro) => [macro.key, nutrition[macro.total] * KCAL_PER_GRAM[macro.key]]),
  )
  const total = Object.values(energy).reduce((sum, kcal) => sum + kcal, 0)
  if (total <= 0) return null
  return Object.fromEntries(MACROS.map((macro) => [macro.key, (energy[macro.key] / total) * 100]))
}

export function inRange(key, percent) {
  const [low, high] = AMDR_PERCENT[key]
  return percent >= low && percent <= high
}

// The meal's calorie target, from whichever stage reported one.
export function mealTarget(plan) {
  const candidates = [
    plan?.macro_balance?.target_meal_calories,
    plan?.reconciliation?.target_meal_calories,
    plan?.meal_plan?.portion_scaling?.target_meal_calories,
  ]
  return candidates.find(isNumber) ?? null
}

export function calories(plan) {
  const nutrition = plan?.nutrition
  if (!nutrition || !isNumber(nutrition.total_calories)) return null
  return {
    total: nutrition.total_calories,
    target: mealTarget(plan),
    grams: Object.fromEntries(
      MACROS.map((macro) => [
        macro.key,
        isNumber(nutrition[macro.total]) ? nutrition[macro.total] : null,
      ]),
    ),
  }
}

// Each data source's verification level, mirroring the service's
// VERIFICATION_BY_SOURCE. An unknown source is an estimate, as it is there.
const VERIFICATION_BY_SOURCE = {
  usda_fooddata_central: 'verified_external',
  fatsecret_platform: 'verified_external',
  trusted_local_reference: 'trusted_local',
  local_reference_table: 'estimated',
  category_estimate: 'estimated',
}

const SOURCE_TAGS = {
  verified_external: 'Verified',
  trusted_local: 'Reference',
  estimated: 'Estimated',
}

function verificationOf(ingredient) {
  if (SOURCE_TAGS[ingredient.verification]) return ingredient.verification
  return VERIFICATION_BY_SOURCE[ingredient.data_source] ?? 'estimated'
}

// The served portions: the verified ingredients when the response has them,
// otherwise the meal definition's, which carry no source to tag.
export function ingredients(plan) {
  const verified = plan?.nutrition?.ingredients_macros
  if (Array.isArray(verified) && verified.length) {
    return verified.map((ingredient) => ({
      name: ingredient.item_name,
      grams: ingredient.base_quantity_grams,
      tag: SOURCE_TAGS[verificationOf(ingredient)],
      estimated: verificationOf(ingredient) === 'estimated',
    }))
  }
  const defined = plan?.meal_plan?.meal_definition?.ingredients
  if (!Array.isArray(defined)) return []
  return defined.map((ingredient) => ({
    name: ingredient.item_name,
    grams: ingredient.base_quantity_grams,
    tag: null,
    estimated: false,
  }))
}

export function estimatedCount(plan) {
  const list = ingredients(plan)
  const estimated = list.filter((ingredient) => ingredient.estimated).length
  return estimated ? { estimated, of: list.length } : null
}

const MATCH_BADGES = {
  matched: { label: 'Close menu match', tone: 'good' },
  fallback: { label: 'Standard meal', tone: 'warn' },
}

export function matchBadge(plan) {
  return MATCH_BADGES[plan?.plan_status] ?? null
}

const kcal = (value) => `${Math.round(value).toLocaleString('en-AU')} kcal`

// "How this plan was made": the service's own notes, in its words, plus the
// daily estimate it sized the meal from. Nothing here is a step the service
// did not report.
export function howItWasMade(plan) {
  const notes = []
  const budget = plan?.calorie_budget
  if (budget && isNumber(budget.estimated_daily_expenditure_kcal)) {
    const target = mealTarget(plan)
    notes.push(
      target === null
        ? `Your estimated daily energy is ${kcal(budget.estimated_daily_expenditure_kcal)}.`
        : `Your estimated daily energy is ${kcal(budget.estimated_daily_expenditure_kcal)}; this meal is sized to ${kcal(target)}.`,
    )
    // The trained model adds a workout the meal request cannot describe; the
    // service fills its defaults (docs/8_design.md §3.1). The rule-based
    // fallback adds none.
    if (budget.model_version && !budget.model_version.startsWith('mifflin_st_jeor')) {
      notes.push(
        'That estimate includes a default 30-minute workout at 100 bpm, because the meal request has no workout details.',
      )
    }
  }
  for (const warnings of [
    plan?.meal_plan?.metadata?.warnings,
    budget?.warnings,
    plan?.nutrition?.metadata?.warnings,
  ]) {
    if (Array.isArray(warnings)) notes.push(...warnings.filter((note) => typeof note === 'string'))
  }
  return [...new Set(notes)]
}
