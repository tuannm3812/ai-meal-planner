import { useId } from 'react'

import { ACTIVITY_OPTIONS, AVOID_OPTIONS, GOAL_OPTIONS, SEX_OPTIONS } from './profile'

const fieldClass =
  'mt-1.5 h-12 w-full rounded-[10px] border bg-surface px-3.5 text-base text-ink outline-none focus:ring-2 focus:ring-ink'

function FieldError({ id, message }) {
  if (!message) return null
  return (
    <p className="mt-1.5 text-sm text-accent-text" id={id}>
      {message}
    </p>
  )
}

function NumberField({ name, label, value, error, onChange, ...inputProps }) {
  const id = useId()
  const errorId = `${id}-error`
  return (
    <div>
      <label className="block text-sm font-medium text-ink" htmlFor={id}>
        {label}
      </label>
      <input
        aria-describedby={error ? errorId : undefined}
        aria-invalid={error ? 'true' : undefined}
        className={`${fieldClass} ${error ? 'border-accent-text' : 'border-line'}`}
        id={id}
        inputMode="decimal"
        name={name}
        onChange={(event) => onChange(event.target.value)}
        type="number"
        value={value}
        {...inputProps}
      />
      <FieldError id={errorId} message={error} />
    </div>
  )
}

function ChoiceField({ label, value, options, error, onChange, className = '' }) {
  const id = useId()
  const errorId = `${id}-error`
  return (
    <div className={className}>
      <label className="block text-sm font-medium text-ink" htmlFor={id}>
        {label}
      </label>
      <select
        aria-describedby={error ? errorId : undefined}
        aria-invalid={error ? 'true' : undefined}
        className={`${fieldClass} ${error ? 'border-accent-text' : 'border-line'}`}
        id={id}
        onChange={(event) => onChange(event.target.value)}
        value={value}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <FieldError id={errorId} message={error} />
    </div>
  )
}

// Step 1 of docs/8_design.md §3.1. Controlled: the profile and its errors
// belong to the caller, which sends them with the meal request.
function ProfileForm({ profile, errors = {}, onChange }) {
  const set = (key) => (value) => onChange({ ...profile, [key]: value })

  const toggleAvoid = (id) => {
    const avoid = profile.avoid.includes(id)
      ? profile.avoid.filter((item) => item !== id)
      : [...profile.avoid, id]
    onChange({ ...profile, avoid })
  }

  return (
    <section
      aria-labelledby="profile-heading"
      className="grid gap-8 rounded-[20px] border border-line bg-surface p-6 sm:p-8 lg:grid-cols-[1fr_300px]"
    >
      <div className="min-w-0">
        <p className="text-sm font-semibold uppercase tracking-wider text-accent-text">
          Step 1 · You
        </p>
        <h2
          className="mt-2 font-display text-3xl font-bold tracking-tight text-ink"
          id="profile-heading"
          tabIndex={-1}
        >
          Tell us about you
        </h2>
        <p className="mt-3 max-w-2xl text-base leading-7 text-muted">
          We use this to estimate how much energy you burn in a day and size your meal to fit
          your goal. Your details go with each plan request, and when the app runs locally the
          server keeps a history of the plans it makes, including these details.
        </p>

        <div className="mt-8 flex flex-col gap-7">
          <fieldset>
            <legend className="mb-3 font-semibold text-ink">Your goal</legend>
            <div className="grid gap-3 sm:grid-cols-3">
              {GOAL_OPTIONS.map((option) => {
                const checked = profile.goal === option.value
                return (
                  <label
                    className={`flex cursor-pointer flex-col gap-1 rounded-[14px] bg-surface p-4 focus-within:ring-2 focus-within:ring-ink ${
                      checked ? 'border-2 border-ink' : 'border border-line'
                    }`}
                    key={option.value}
                  >
                    <span className="flex items-center gap-2 font-semibold text-ink">
                      <input
                        checked={checked}
                        className="h-4 w-4 accent-ink"
                        name="goal"
                        onChange={() => set('goal')(option.value)}
                        type="radio"
                        value={option.value}
                      />
                      {option.label}
                    </span>
                    <span className="text-sm text-muted">{option.description}</span>
                  </label>
                )
              })}
            </div>
            <FieldError message={errors.goal} />
          </fieldset>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <NumberField
              error={errors.age}
              label="Age"
              name="age"
              onChange={set('age')}
              value={profile.age}
            />
            <ChoiceField
              error={errors.sex}
              label="Sex"
              onChange={set('sex')}
              options={SEX_OPTIONS}
              value={profile.sex}
            />
            <NumberField
              error={errors.heightCm}
              label="Height (cm)"
              name="height_cm"
              onChange={set('heightCm')}
              value={profile.heightCm}
            />
            <NumberField
              error={errors.weightKg}
              label="Weight (kg)"
              name="weight_kg"
              onChange={set('weightKg')}
              value={profile.weightKg}
            />
          </div>

          <ChoiceField
            className="max-w-md"
            error={errors.activity}
            label="How active are you?"
            onChange={set('activity')}
            options={ACTIVITY_OPTIONS}
            value={profile.activity}
          />

          <fieldset>
            <legend className="font-semibold text-ink">
              Anything to avoid? <span className="font-normal text-muted">(optional)</span>
            </legend>
            <p className="mb-3 mt-1 text-sm text-muted">
              Meals with a conflicting ingredient are left out.
            </p>
            <div className="flex flex-wrap gap-2">
              {AVOID_OPTIONS.map((option) => (
                <label
                  className="flex min-h-[44px] cursor-pointer items-center gap-2 rounded-full border border-line bg-surface px-3.5 text-sm text-ink focus-within:ring-2 focus-within:ring-ink has-[:checked]:border-ink has-[:checked]:bg-success-bg"
                  key={option.id}
                >
                  <input
                    checked={profile.avoid.includes(option.id)}
                    className="h-4 w-4 accent-ink"
                    onChange={() => toggleAvoid(option.id)}
                    type="checkbox"
                  />
                  {option.label}
                </label>
              ))}
            </div>
            <FieldError message={errors.avoid} />
          </fieldset>
        </div>
      </div>

      <aside
        aria-label="How your meal is sized"
        className="self-start rounded-[20px] bg-ink p-7 text-ground"
      >
        <p className="text-sm text-ground/75">How your meal is sized</p>
        <ol className="mt-4 flex list-decimal flex-col gap-3.5 pl-5 text-base leading-6">
          <li>A trained model estimates the energy you burn in a day.</li>
          <li>Your goal sets the calories for this meal, with a safe floor when losing weight.</li>
          <li>Portions are resized so protein, carbs and fat sit inside recommended ranges.</li>
          <li>Nutrition is checked against food data, and anything estimated is labelled.</li>
        </ol>
        <p className="mt-6 border-t border-ground/20 pt-4 text-sm text-ground/75">
          A planning aid, not medical advice.
        </p>
      </aside>
    </section>
  )
}

export default ProfileForm
