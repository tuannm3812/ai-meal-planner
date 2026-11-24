import { useId, useState } from 'react'

import { predictCalorieExpenditure } from '../../api/mealPlanner'
import Icon from '../../components/icons/Icon'
import { Calculator, CircleAlert } from '../../components/icons/glyphs'
import ErrorBanner from '../../components/ui/ErrorBanner'
import Note from '../../components/ui/Note'
import { card, primaryButton } from '../../components/ui/styles'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import {
  ACTIVITY_OPTIONS,
  DEFAULT_PROFILE,
  GOAL_OPTIONS,
  SEX_OPTIONS,
  WORKOUT_OPTIONS,
  validateProfile,
  workoutToRequest,
} from '../profile/profile'
import CalorieResult from './CalorieResult'

// The estimate's goal names differ from the profile's.
const GOAL_TO_REQUEST = { lose: 'weight_loss', maintain: 'maintain', gain: 'muscle_gain' }

const fieldClass =
  'mt-1.5 h-12 w-full rounded-[10px] border border-line bg-surface px-3.5 text-base text-ink outline-none focus:ring-2 focus:ring-ink'

function Field({ label, error, children }) {
  const id = useId()
  return (
    <div>
      <label className="block text-sm font-medium text-ink" htmlFor={id}>
        {label}
      </label>
      {children(id)}
      {error && (
        <p className="mt-1.5 flex items-start gap-1.5 text-sm font-medium text-danger-fg">
          <Icon as={CircleAlert} className="mt-px" size="sm" />
          {error}
        </p>
      )}
    </div>
  )
}

function Choice({ label, value, options, error, onChange }) {
  return (
    <Field error={error} label={label}>
      {(id) => (
        <select className={fieldClass} id={id} onChange={(event) => onChange(event.target.value)} value={value}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      )}
    </Field>
  )
}

function NumberInput({ label, value, error, onChange, placeholder }) {
  return (
    <Field error={error} label={label}>
      {(id) => (
        <input
          className={fieldClass}
          id={id}
          inputMode="decimal"
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          type="text"
          value={value}
        />
      )}
    </Field>
  )
}

// The calorie model on its own. It takes the same fields as the profile, in
// the same words, and sends today's workout the same way a plan does, so the
// same details give the same numbers here and on the plan page. `initial` is
// the person's profile; nothing typed here changes it.
function CaloriesTab({ initial = {} }) {
  const [details, setDetails] = useState({ ...DEFAULT_PROFILE, ...initial, avoid: [] })
  const [errors, setErrors] = useState({})
  const set = (key) => (value) => setDetails((current) => ({ ...current, [key]: value }))
  const {
    data: result,
    error,
    isLoading,
    run: requestExpenditure,
    reset: clearResult,
  } = useAsyncRequest(
    predictCalorieExpenditure,
    'Could not estimate your calories. Check your connection and try again.',
  )

  const handleSubmit = async (event) => {
    event.preventDefault()
    const found = validateProfile(details)
    setErrors(found)
    if (Object.keys(found).length) return
    clearResult()
    await requestExpenditure({
      age: Number(details.age),
      sex: details.sex,
      height_cm: Number(details.heightCm),
      weight_kg: Number(details.weightKg),
      activity_multiplier: Number(details.activity),
      ...workoutToRequest(details),
      goal: GOAL_TO_REQUEST[details.goal],
    })
  }

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,460px)_minmax(0,1fr)]">
      <section aria-labelledby="estimate-details" className={`${card} lg:sticky lg:top-6`}>
        <h2 className="font-display text-[20px] font-extrabold tracking-tight text-ink" id="estimate-details">
          Details for this estimate
        </h2>
        <p className="mt-1 text-sm leading-6 text-muted">The same calorie model that sizes your meals.</p>

        <form className="mt-6 flex flex-col gap-5" noValidate onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <NumberInput error={errors.age} label="Age" onChange={set('age')} value={details.age} />
            <Choice error={errors.sex} label="Sex" onChange={set('sex')} options={SEX_OPTIONS} value={details.sex} />
            <NumberInput
              error={errors.heightCm}
              label="Height (cm)"
              onChange={set('heightCm')}
              value={details.heightCm}
            />
            <NumberInput
              error={errors.weightKg}
              label="Weight (kg)"
              onChange={set('weightKg')}
              value={details.weightKg}
            />
          </div>
          <Choice
            error={errors.activity}
            label="How active are you?"
            onChange={set('activity')}
            options={ACTIVITY_OPTIONS}
            value={details.activity}
          />
          <Choice
            error={errors.workout}
            label="Today's workout"
            onChange={set('workout')}
            options={WORKOUT_OPTIONS}
            value={details.workout}
          />
          {details.workout === 'trained' && (
            <div className="grid grid-cols-2 gap-4">
              <NumberInput
                error={errors.workoutMinutes}
                label="Minutes"
                onChange={set('workoutMinutes')}
                value={details.workoutMinutes}
              />
              <NumberInput
                error={errors.heartRate}
                label="Heart rate (optional)"
                onChange={set('heartRate')}
                placeholder="bpm"
                value={details.heartRate}
              />
            </div>
          )}
          <Choice
            error={errors.goal}
            label="Your goal"
            onChange={set('goal')}
            options={GOAL_OPTIONS}
            value={details.goal}
          />
          <button className={`${primaryButton} w-full`} disabled={isLoading} type="submit">
            <Icon as={Calculator} size="sm" />
            {isLoading ? 'Estimating…' : 'Estimate my calories'}
          </button>
        </form>

        {error && (
          <div className="mt-5">
            <ErrorBanner>{error}</ErrorBanner>
          </div>
        )}
      </section>

      <div className="flex min-w-0 flex-col gap-6">
        {result ? (
          <CalorieResult result={result} />
        ) : (
          <section aria-live="polite" className={card}>
            <h2 className="font-display text-[20px] font-extrabold tracking-tight text-ink">
              {isLoading ? 'Estimating your calories…' : 'What you burn in a day'}
            </h2>
            <p className="mt-2 max-w-xl text-muted">
              Press the button to see the calories you burn in a day, the daily target for your
              goal, and the size of one meal.
            </p>
            <Note className="mt-4">
              Today&rsquo;s workout replaces your usual week&rsquo;s exercise, so a rest day counts as one.
            </Note>
          </section>
        )}
      </div>
    </div>
  )
}

export default CaloriesTab
