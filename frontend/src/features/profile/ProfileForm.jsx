import SizingPanel from './SizingPanel'
import { useId } from 'react'

import Icon from '../../components/icons/Icon'
import { CircleAlert, Scale, Timer, TrendingDown, TrendingUp } from '../../components/icons/glyphs'
import Note from '../../components/ui/Note'
import {
  ACTIVITY_OPTIONS,
  AVOID_OPTIONS,
  GOAL_OPTIONS,
  PROFILE_DISCLOSURE,
  SEX_OPTIONS,
  WORKOUT_OPTIONS,
} from './profile'

const fieldClass =
  'mt-1.5 h-12 w-full rounded-[10px] border bg-surface px-3.5 text-base text-ink outline-none focus:ring-2 focus:ring-ink'

function FieldError({ id, message }) {
  if (!message) return null
  return (
    <p className="mt-1.5 flex items-start gap-1.5 text-sm font-medium text-danger-fg" id={id}>
      <Icon as={CircleAlert} className="mt-px" size="sm" />
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
        className={`${fieldClass} ${error ? 'border-danger-fg' : 'border-line'}`}
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
        className={`${fieldClass} ${error ? 'border-danger-fg' : 'border-line'}`}
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

// One numbered row of the form: the step's name on the left, its fields on
// the right, so every field starts on the same edge.
function Step({ number, title, hint, group = false, children }) {
  const id = useId()
  return (
    <div
      aria-labelledby={group ? id : undefined}
      className="grid gap-x-8 gap-y-4 py-7 md:grid-cols-[220px_minmax(0,1fr)]"
      role={group ? 'group' : undefined}
    >
      <div className="flex items-start gap-3">
        <span
          aria-hidden="true"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-tint font-display text-sm font-extrabold text-cobalt"
        >
          {number}
        </span>
        <div className="pt-1.5">
          <p className="font-semibold leading-6 text-ink" id={id}>
            {title}
          </p>
          {hint && <p className="mt-1 text-sm leading-5 text-muted">{hint}</p>}
        </div>
      </div>
      <div className="min-w-0">{children}</div>
    </div>
  )
}

const GOAL_GLYPHS = { lose: TrendingDown, maintain: Scale, gain: TrendingUp }

// The profile of docs/8_design.md §3.1, on the first visit and the Profile
// page, drawn as an order ticket (DEC-44): a tinted header, numbered rows
// split by dashed lines, and an optional footer for the caller's button.
// Controlled: the profile and its errors belong to the caller, which sends
// them with the meal request. The welcome page passes a shorter intro, an h2
// under its own h1, and no sizing panel, because the page around it already
// says how a meal is sized.
function ProfileForm({
  profile,
  errors = {},
  onChange,
  eyebrow = 'Your details',
  title = 'Tell us about you',
  headingLevel = 1,
  intro = PROFILE_DISCLOSURE,
  badge = null,
  footer = null,
  showSizing = true,
  children,
}) {
  const Heading = headingLevel === 2 ? 'h2' : 'h1'
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
      className={`grid gap-8 ${showSizing ? '2xl:grid-cols-[minmax(0,1fr)_300px]' : ''}`}
    >
      <div className="min-w-0 overflow-hidden rounded-3xl border border-ink bg-surface">
        <header className="flex flex-wrap items-end justify-between gap-x-8 gap-y-4 bg-tint px-6 py-7 sm:px-8">
          <div className="min-w-0">
            <p className="text-sm font-semibold uppercase tracking-wider text-accent-text">{eyebrow}</p>
            <Heading
              className="mt-2 font-display text-3xl font-extrabold tracking-tight text-ink sm:text-4xl"
              id="profile-heading"
              tabIndex={-1}
            >
              {title}
            </Heading>
            <p className="mt-3 max-w-2xl text-base leading-7 text-muted">{intro}</p>
          </div>
          {badge && (
            <p className="flex items-center gap-2 rounded-full bg-surface px-4 py-2 text-sm font-semibold text-ink">
              <Icon as={Timer} size="sm" tone="light" />
              {badge}
            </p>
          )}
        </header>

        <div className="divide-y divide-dashed divide-line px-6 sm:px-8">
          <Step group number={1} title="Your goal">
            <div className="grid grid-cols-[repeat(auto-fit,minmax(118px,1fr))] gap-3">
              {GOAL_OPTIONS.map((option) => {
                const checked = profile.goal === option.value
                return (
                  <label
                    className={`flex cursor-pointer flex-col gap-1.5 rounded-2xl border-2 p-4 focus-within:ring-2 focus-within:ring-ink focus-within:ring-offset-2 ${
                      checked ? 'border-ink bg-tint' : 'border-line bg-surface hover:border-muted'
                    }`}
                    key={option.value}
                  >
                    <Icon as={GOAL_GLYPHS[option.value]} tone="light" />
                    <span className="flex items-center gap-2 font-semibold text-ink">
                      <input
                        checked={checked}
                        className="h-4 w-4 shrink-0 accent-ink"
                        name="goal"
                        onChange={() => set('goal')(option.value)}
                        type="radio"
                        value={option.value}
                      />
                      {option.label}
                    </span>
                    <span className="text-sm leading-5 text-muted">{option.description}</span>
                  </label>
                )
              })}
            </div>
            <FieldError message={errors.goal} />
          </Step>

          <Step number={2} title="Your body">
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
          </Step>

          <Step number={3} title="Your activity">
            <div className="grid gap-4 sm:grid-cols-2">
              <ChoiceField
                error={errors.activity}
                label="How active are you?"
                onChange={set('activity')}
                options={ACTIVITY_OPTIONS}
                value={profile.activity}
              />
              <ChoiceField
                error={errors.workout}
                label="Today's workout"
                onChange={set('workout')}
                options={WORKOUT_OPTIONS}
                value={profile.workout}
              />
            </div>
            {profile.workout === 'trained' && (
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <NumberField
                  error={errors.workoutMinutes}
                  label="Minutes"
                  name="duration_minutes"
                  onChange={set('workoutMinutes')}
                  value={profile.workoutMinutes}
                />
                <NumberField
                  error={errors.heartRate}
                  label="Average heart rate (optional)"
                  name="heart_rate_bpm"
                  onChange={set('heartRate')}
                  placeholder="bpm"
                  value={profile.heartRate}
                />
              </div>
            )}
            <Note className="mt-4">
              Your activity level covers a usual week. When you give today's workout, it takes the
              place of that week's exercise, so a rest day counts as one.
            </Note>
          </Step>

          <Step
            group
            hint="Meals with a conflicting ingredient are left out."
            number={4}
            title={
              <>
                Anything to avoid? <span className="font-normal text-muted">(optional)</span>
              </>
            }
          >
            <div className="flex flex-wrap gap-2">
              {AVOID_OPTIONS.map((option) => (
                <label
                  className="flex min-h-[44px] cursor-pointer items-center gap-2 rounded-full border-2 border-line bg-surface px-4 text-sm font-medium text-ink hover:border-muted focus-within:ring-2 focus-within:ring-ink focus-within:ring-offset-2 has-[:checked]:border-ink has-[:checked]:bg-tint"
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
          </Step>

          {children && (
            <Step number={5} title="Your store">
              {children}
            </Step>
          )}
        </div>

        {footer && (
          <div className="border-t-2 border-dashed border-line bg-ground px-6 py-7 sm:px-8">{footer}</div>
        )}
      </div>

      {showSizing && <SizingPanel />}
    </section>
  )
}

export default ProfileForm
