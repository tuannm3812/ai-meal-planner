// The "Craving" step of docs/8_design.md §3.2: what the person asks for and
// where they shop, with MealRequest's bounds.

// Each suggestion is a real meal in data/meal_corpus/meals.json, so picking
// one is a craving the menu can answer. craving.test.js checks every `meal`
// against the corpus.
export const CRAVING_SUGGESTIONS = [
  { label: 'Salmon quinoa', meal: 'Salmon Quinoa Plate' },
  { label: 'Chickpea curry', meal: 'Chickpea Curry Bowl' },
  { label: 'Banana oat bowl', meal: 'Banana Oat Protein Bowl' },
  { label: 'Tofu fried rice', meal: 'Tofu Fried Rice' },
  { label: 'Beef taco salad', meal: 'Beef Taco Salad' },
  { label: 'Greek chicken bowl', meal: 'Greek Chicken Bowl' },
]

// Mirrors MealRequest in backend/app/schemas/requests.py.
const TEXT_FIELDS = [
  { key: 'craving', label: 'craving', min: 2, max: 180 },
  { key: 'location', label: 'location', min: 2, max: 160 },
  { key: 'userId', label: 'user ID', min: 3, max: 80 },
]

const REQUEST_FIELD_TO_KEY = { craving: 'craving', location: 'location', user_id: 'userId' }

// An empty craving is the starting state, not a mistake, so it gets no
// message; the plan button simply stays off. Every other field starts filled,
// so emptying it is worth saying.
export function validateRequest(values) {
  const errors = {}
  for (const field of TEXT_FIELDS) {
    const value = String(values[field.key] ?? '').trim()
    if (!value) {
      if (field.key !== 'craving') errors[field.key] = `Enter a ${field.label}.`
    } else if (value.length < field.min) {
      errors[field.key] = `Use at least ${field.min} characters.`
    } else if (value.length > field.max) {
      errors[field.key] = `Use at most ${field.max} characters (now ${value.length}).`
    }
  }
  return errors
}

// The craving, location and user ID errors in a FastAPI 422, keyed like
// validateRequest, or null when it names none of them.
export function requestErrorsFrom422(detail) {
  if (!Array.isArray(detail)) return null
  const errors = {}
  for (const item of detail) {
    const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null
    const key = REQUEST_FIELD_TO_KEY[field]
    if (key && !errors[key]) errors[key] = item.msg || 'The service rejected this value.'
  }
  return Object.keys(errors).length ? errors : null
}
