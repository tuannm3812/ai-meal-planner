// The "You" step of docs/8_design.md §3.1: the MealRequest profile fields,
// their bounds, and how the avoid-chips map onto the request.
//
// The profile lives in React state only. Nothing here touches the URL or
// browser storage: health fields in a URL reach access logs, and storage
// would be persistence the screen does not disclose.

export const GOAL_OPTIONS = [
  { value: 'lose', label: 'Lose weight', description: 'A gentle deficit, never below a safe floor' },
  { value: 'maintain', label: 'Maintain', description: 'Eat about what you burn' },
  { value: 'gain', label: 'Gain', description: 'A modest surplus for building' },
]

export const SEX_OPTIONS = [
  { value: 'female', label: 'Female' },
  { value: 'male', label: 'Male' },
]

// Plain-language activity levels and the multipliers the service expects
// (MealRequest.activity_multiplier: > 1.0 and <= 2.5).
export const ACTIVITY_OPTIONS = [
  { value: '1.2', label: 'Mostly sitting (little or no exercise)' },
  { value: '1.375', label: 'Lightly active (exercise 1–3 days a week)' },
  { value: '1.55', label: 'Moderately active (exercise 3–5 days a week)' },
  { value: '1.725', label: 'Very active (hard exercise 6–7 days a week)' },
  { value: '1.9', label: 'Extra active (physical job or training twice a day)' },
]

// Today's workout (P5, DEC-33). The activity level describes a usual week; a
// stated workout or rest day replaces that week's exercise (DEC-40). "Not sure"
// sends nothing, so the service keeps the activity level, adds its default
// workout and the plan says so.
export const WORKOUT_OPTIONS = [
  { value: 'unsure', label: 'Not sure (assume a 30-minute workout)' },
  { value: 'rest', label: 'Rest day, no workout' },
  { value: 'trained', label: 'I worked out' },
]

// Only values backend/app/rag/rules.py already enforces. Diabetes is not
// offered: the rules have no diabetes handling, so offering it would imply a
// filter that does not exist.
export const AVOID_OPTIONS = [
  { id: 'vegetarian', label: 'Vegetarian', field: 'dietary_preferences', value: 'vegetarian' },
  { id: 'vegan', label: 'Vegan', field: 'dietary_preferences', value: 'vegan' },
  { id: 'dairy-free', label: 'Dairy-free', field: 'dietary_preferences', value: 'dairy-free' },
  { id: 'gluten-free', label: 'Gluten-free', field: 'dietary_preferences', value: 'gluten-free' },
  { id: 'peanut', label: 'Peanut allergy', field: 'health_conditions', value: 'peanut allergy' },
  { id: 'kidney', label: 'Kidney disease', field: 'health_conditions', value: 'kidney disease' },
]

// Number inputs hold strings while the person types; they become numbers only
// in the request.
export const DEFAULT_PROFILE = {
  goal: 'maintain',
  age: '34',
  sex: 'female',
  heightCm: '168',
  weightKg: '64',
  activity: '1.55',
  workout: 'unsure',
  workoutMinutes: '30',
  heartRate: '',
  avoid: [],
}

// Mirrors MealRequest's bounds in backend/app/schemas/requests.py, so a
// request the screen sends is one the service accepts.
const NUMBER_FIELDS = [
  { key: 'age', label: 'Age', min: 0, max: 120, integer: true, unit: 'years' },
  { key: 'heightCm', label: 'Height', min: 80, max: 260, unit: 'cm' },
  { key: 'weightKg', label: 'Weight', min: 20, max: 350, unit: 'kg' },
]

// The request field each profile key is sent as, so a 422 can be mapped back.
export const REQUEST_FIELD_TO_PROFILE_KEY = {
  goal: 'goal',
  age: 'age',
  sex: 'sex',
  height_cm: 'heightCm',
  weight_kg: 'weightKg',
  activity_multiplier: 'activity',
  duration_minutes: 'workoutMinutes',
  heart_rate_bpm: 'heartRate',
  dietary_preferences: 'avoid',
  health_conditions: 'avoid',
}

export function validateProfile(profile) {
  const errors = {}
  for (const field of NUMBER_FIELDS) {
    const raw = String(profile[field.key] ?? '').trim()
    if (!raw) {
      errors[field.key] = `Enter your ${field.label.toLowerCase()}.`
      continue
    }
    const value = Number(raw)
    if (!Number.isFinite(value)) {
      errors[field.key] = `${field.label} must be a number.`
    } else if (field.integer && !Number.isInteger(value)) {
      errors[field.key] = `${field.label} must be a whole number.`
    } else if (value <= field.min || value > field.max) {
      errors[field.key] =
        `${field.label} must be more than ${field.min} and at most ${field.max} ${field.unit}.`
    }
  }
  if (!GOAL_OPTIONS.some((option) => option.value === profile.goal)) {
    errors.goal = 'Choose a goal.'
  }
  if (!SEX_OPTIONS.some((option) => option.value === profile.sex)) {
    errors.sex = 'Choose a sex.'
  }
  if (!ACTIVITY_OPTIONS.some((option) => option.value === profile.activity)) {
    errors.activity = 'Choose how active you are.'
  }
  if (!WORKOUT_OPTIONS.some((option) => option.value === profile.workout)) {
    errors.workout = 'Choose what you did today.'
  } else if (profile.workout === 'trained') {
    Object.assign(errors, validateWorkout(profile))
  }
  return errors
}

// Mirrors MealRequest.duration_minutes (0 to 600; 0 is the rest-day option)
// and heart_rate_bpm (> 20 and <= 240, optional).
function validateWorkout(profile) {
  const errors = {}
  const minutes = String(profile.workoutMinutes ?? '').trim()
  const value = Number(minutes)
  if (!minutes) {
    errors.workoutMinutes = 'Enter how many minutes you worked out.'
  } else if (!Number.isFinite(value)) {
    errors.workoutMinutes = 'Workout length must be a number.'
  } else if (value <= 0 || value > 600) {
    errors.workoutMinutes = 'Workout length must be more than 0 and at most 600 minutes.'
  }
  const heartRate = String(profile.heartRate ?? '').trim()
  const bpm = Number(heartRate)
  if (heartRate && !Number.isFinite(bpm)) {
    errors.heartRate = 'Heart rate must be a number.'
  } else if (heartRate && (bpm <= 20 || bpm > 240)) {
    errors.heartRate = 'Heart rate must be more than 20 and at most 240 bpm.'
  }
  return errors
}

// The MealRequest fields this profile contributes.
export function profileToRequest(profile) {
  const chosen = AVOID_OPTIONS.filter((option) => profile.avoid.includes(option.id))
  return {
    goal: profile.goal,
    age: Number(profile.age),
    sex: profile.sex,
    height_cm: Number(profile.heightCm),
    weight_kg: Number(profile.weightKg),
    activity_multiplier: Number(profile.activity),
    ...workoutToRequest(profile),
    dietary_preferences: chosen
      .filter((option) => option.field === 'dietary_preferences')
      .map((option) => option.value),
    health_conditions: chosen
      .filter((option) => option.field === 'health_conditions')
      .map((option) => option.value),
  }
}

// The workout fields, sent only when the person gave them.
function workoutToRequest(profile) {
  if (profile.workout === 'rest') return { duration_minutes: 0 }
  if (profile.workout !== 'trained') return {}
  const heartRate = String(profile.heartRate ?? '').trim()
  return {
    duration_minutes: Number(profile.workoutMinutes),
    ...(heartRate ? { heart_rate_bpm: Number(heartRate) } : {}),
  }
}

// Two profiles ask for the same plan when their requests are identical, so
// typing "64" over "64" or ticking and unticking a chip is not a change.
export function sameRequest(a, b) {
  return JSON.stringify(profileToRequest(a)) === JSON.stringify(profileToRequest(b))
}

// The request fields each profile key is sent as.
const PROFILE_KEY_TO_REQUEST_FIELDS = Object.entries(REQUEST_FIELD_TO_PROFILE_KEY).reduce(
  (fields, [field, key]) => ({ ...fields, [key]: [...(fields[key] || []), field] }),
  {},
)

// The errors whose profile field still sends what it sent when they were
// reported. Editing one field clears only that field's server error.
export function errorsForUnchangedFields(errors, profile, submitted) {
  if (!errors || !submitted) return null
  const now = profileToRequest(profile)
  const then = profileToRequest(submitted)
  const kept = Object.fromEntries(
    Object.entries(errors).filter(([key]) =>
      PROFILE_KEY_TO_REQUEST_FIELDS[key].every(
        (field) => JSON.stringify(now[field]) === JSON.stringify(then[field]),
      ),
    ),
  )
  return Object.keys(kept).length ? kept : null
}

// FastAPI's 422 detail is a list of {loc: ['body', field], msg}. Returns the
// profile keys it names, each with the service's message, or null when the
// detail is not that shape or names no profile field.
export function profileErrorsFrom422(detail) {
  if (!Array.isArray(detail)) return null
  const errors = {}
  for (const item of detail) {
    const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null
    const key = REQUEST_FIELD_TO_PROFILE_KEY[field]
    if (key && !errors[key]) errors[key] = item.msg || 'The service rejected this value.'
  }
  return Object.keys(errors).length ? errors : null
}

// What happens to the details, said wherever they are asked for (docs/8_design.md §3.1).
export const PROFILE_DISCLOSURE =
  "We use this to estimate how much energy you burn in a day and size your meal to fit your goal. " +
  "This browser keeps your details so you don't retype them. They go with each plan request, and " +
  'when the app runs locally the server keeps a history of the plans it makes, including these ' +
  'details.'
