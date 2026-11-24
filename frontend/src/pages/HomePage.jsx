import { Link, useNavigate } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import {
  ArrowRight,
  Bookmark,
  History,
  Search,
  Timer,
} from '../components/icons/glyphs'
import BlobShape from '../components/illustrations/BlobShape'
import DishIllustration from '../components/illustrations/DishIllustration'
import { dishType } from '../components/illustrations/dishType'
import PriceTag from '../components/ui/PriceTag'
import { pageShell, primaryButton, sectionHeading } from '../components/ui/styles'
import { CRAVING_SUGGESTIONS } from '../features/craving/craving'
import { planSummary } from '../features/meals/meals'
import MacroBar from '../features/plan/charts/MacroBar'
import MealGrid from '../features/meals/MealGrid'
import { useMealLists } from '../features/meals/useMealLists'
import WelcomePage from './WelcomePage'

// Today's workout, as three chips under the craving (DEC-33, DEC-40). It is
// the profile's own field, so Profile shows the same answer.
const WORKOUT_CHIPS = [
  { value: 'unsure', label: 'Not sure' },
  { value: 'rest', label: 'Rest day' },
  { value: 'trained', label: 'I worked out' },
]

function WorkoutChips() {
  const { profile, setProfile, profileErrors } = usePlannerContext()
  return (
    <fieldset className="flex flex-wrap items-center gap-x-3 gap-y-2">
      <legend className="float-left mr-3 flex min-h-[44px] items-center gap-2 text-sm text-on-ink-muted">
        <Icon as={Timer} size="sm" tone="ink" />
        Today&rsquo;s workout
      </legend>
      {WORKOUT_CHIPS.map((chip) => (
        <label
          className="flex min-h-[44px] cursor-pointer items-center rounded-full border border-white/40 px-4 text-sm font-medium text-white hover:bg-white/10 has-[:checked]:border-peach has-[:checked]:bg-peach has-[:checked]:text-ink has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-peach has-[:focus-visible]:ring-offset-2 has-[:focus-visible]:ring-offset-cobalt"
          key={chip.value}
        >
          <input
            checked={profile.workout === chip.value}
            className="sr-only"
            name="home-workout"
            onChange={() => setProfile({ ...profile, workout: chip.value })}
            type="radio"
            value={chip.value}
          />
          {chip.label}
        </label>
      ))}
      {profile.workout === 'trained' && (
        <label className="flex min-h-[44px] items-center gap-2 text-sm text-white">
          <span>for</span>
          <input
            aria-describedby={profileErrors.workoutMinutes ? 'home-workout-error' : undefined}
            aria-invalid={profileErrors.workoutMinutes ? 'true' : undefined}
            aria-label="Workout minutes"
            className="h-11 w-20 rounded-xl border-0 bg-surface px-3 text-[15px] text-ink outline-none focus-visible:ring-2 focus-visible:ring-peach"
            inputMode="numeric"
            onChange={(event) => setProfile({ ...profile, workoutMinutes: event.target.value })}
            value={profile.workoutMinutes}
          />
          <span>minutes</span>
        </label>
      )}
      {profile.workout === 'trained' && profileErrors.workoutMinutes && (
        <p className="basis-full text-sm text-danger-on-ink" id="home-workout-error">
          {profileErrors.workoutMinutes}
        </p>
      )}
      {profile.workout === 'unsure' && (
        <p className="basis-full text-sm text-on-ink-muted">We&rsquo;ll assume a 30-minute workout.</p>
      )}
    </fieldset>
  )
}

function CravingBanner() {
  const planner = usePlannerContext()
  const navigate = useNavigate()
  const { craving, setCraving, canSubmit, requestFieldErrors, retryPause, location, plan } = planner
  const target = plan?.macro_balance?.target_meal_calories

  const submit = async (event) => {
    event.preventDefault()
    if (!canSubmit) return
    navigate('/plan')
    await planner.submitPlan()
  }

  return (
    <section aria-labelledby="home-heading" className="relative overflow-hidden bg-cobalt text-white">
      <div className={`${pageShell} relative flex flex-wrap items-center gap-8 pb-8 pt-10`}>
        <div className="flex min-w-0 flex-[3_1_480px] flex-col gap-5">
          <h1
            className="font-display text-4xl font-extrabold leading-[1.02] tracking-tight sm:text-[58px]"
            id="home-heading"
          >
            What do you feel like <span className="text-peach">eating?</span>
          </h1>
          <form className="flex flex-col gap-3" noValidate onSubmit={submit}>
            <div className="flex flex-wrap gap-3">
              <div className="flex min-h-[64px] flex-[1_1_320px] items-center gap-3 rounded-2xl bg-surface px-5 text-ink focus-within:ring-2 focus-within:ring-peach">
                <Icon as={Search} tone="light" />
                <label className="sr-only" htmlFor="craving-input">
                  Your craving
                </label>
                <input
                  aria-describedby={requestFieldErrors.craving && craving ? 'craving-error' : undefined}
                  aria-invalid={requestFieldErrors.craving && craving ? 'true' : undefined}
                  className="min-w-0 flex-1 border-0 bg-transparent text-[19px] text-ink outline-none placeholder:text-muted"
                  id="craving-input"
                  onChange={(event) => setCraving(event.target.value)}
                  placeholder="Something warm with chicken and rice"
                  value={craving}
                />
              </div>
              <button className={`${primaryButton} min-h-[64px] px-8 text-lg`} disabled={!canSubmit} type="submit">
                Plan my meal
              </button>
            </div>
            {requestFieldErrors.craving && craving && (
              <p className="text-sm text-danger-on-ink" id="craving-error">
                {requestFieldErrors.craving}
              </p>
            )}
            {requestFieldErrors.location && (
              <p className="text-sm text-danger-on-ink">
                {requestFieldErrors.location}{' '}
                <Link className="underline" to="/profile">
                  Fix it on your profile
                </Link>
              </p>
            )}
            {retryPause.active && (
              <p className="text-sm text-danger-on-ink">
                The server asked for a pause. You can plan again in about {retryPause.seconds}{' '}
                seconds.
              </p>
            )}
          </form>
          <WorkoutChips />
          {/* From 1,280 px the rail's "Sized for you" card says this. */}
          <p className="text-sm text-on-ink-muted xl:hidden">
            {typeof target === 'number' ? `Sized for you: about ${Math.round(target)} kcal a meal. ` : 'Sized for you. '}
            Shopping near {location.trim() || 'your area'}.{' '}
            <Link className="text-white underline underline-offset-4" to="/profile">
              Change your details
            </Link>
          </p>
        </div>
        <div aria-hidden="true" className="relative hidden w-[360px] shrink-0 md:block">
          <BlobShape className="absolute -left-8 -top-16 w-[420px]" />
          <DishIllustration className="relative w-[360px]" type="rice" />
        </div>
      </div>
      <div className={`${pageShell} relative pb-10`}>
        <p className="text-sm text-on-ink-muted" id="craving-suggestions">
          Or try one of these
        </p>
        <ul
          aria-labelledby="craving-suggestions"
          className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6"
        >
          {CRAVING_SUGGESTIONS.map((suggestion) => (
            <li className="flex" key={suggestion.meal}>
              <button
                className="flex w-full flex-col items-center gap-2 rounded-2xl bg-surface p-3 text-center text-[15px] font-semibold text-ink hover:ring-2 hover:ring-peach focus:outline-none focus-visible:ring-2 focus-visible:ring-peach focus-visible:ring-offset-2 focus-visible:ring-offset-cobalt"
                onClick={() => setCraving(suggestion.label.toLowerCase())}
                type="button"
              >
                <DishIllustration
                  className="h-[72px] w-full rounded-xl bg-tint sm:h-[88px]"
                  type={dishType(suggestion.meal)}
                />
                {suggestion.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

const average = (values) => Math.round(values.reduce((sum, value) => sum + value, 0) / values.length)

// The right-hand column on wide screens: the plan in hand (or the latest
// one), then this device's numbers so far. Every number comes from the service.
function ContextColumn({ lists }) {
  const planner = usePlannerContext()
  const current = planner.submitted && planner.plan?.meal_plan ? planSummary(planner.plan) : null
  const latest = current ?? lists.history[0] ?? null
  const energies = lists.history.map((meal) => meal.kcal).filter((kcal) => kcal !== null)
  const stats = [
    { label: 'Plans made', value: lists.history.length },
    { label: 'Meals saved', value: lists.saved.length },
    { label: 'Average meal', value: energies.length ? `${average(energies)} kcal` : 'None yet' },
  ]

  return (
    <aside aria-label="Your plan and numbers" className="flex min-w-0 flex-col gap-6 xl:order-last">
      <section aria-labelledby="latest-heading" className="rounded-3xl border border-ink bg-surface p-5">
        <h2 className="font-display text-[20px] font-extrabold tracking-tight text-ink" id="latest-heading">
          {current ? 'Your plan' : 'Latest plan'}
        </h2>
        {latest ? (
          <div className="mt-3 flex flex-col gap-3">
            <DishIllustration
              className="h-[120px] w-full rounded-2xl bg-tint"
              mealName={latest.name}
              type={latest.dish ?? undefined}
            />
            <p className="text-lg font-semibold text-ink">{latest.name ?? 'Untitled meal'}</p>
            {latest.kcal !== null && (
              <PriceTag className="w-fit font-mono" tone="accent">
                {latest.kcal} kcal
              </PriceTag>
            )}
            {latest.split && <MacroBar split={latest.split} withKey />}
            <Link
              className="inline-flex min-h-[48px] items-center justify-between gap-3 rounded-2xl bg-tint px-4 font-semibold text-ink hover:ring-2 hover:ring-cobalt focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
              to={current ? '/plan' : `/plans/${encodeURIComponent(latest.requestId)}`}
            >
              {current ? 'Back to your plan' : 'Open this plan'}
              <Icon as={ArrowRight} size="sm" />
            </Link>
          </div>
        ) : planner.submitted ? (
          <Link
            className="mt-3 inline-flex min-h-[48px] w-full items-center justify-between gap-3 rounded-2xl bg-tint px-4 font-semibold text-ink hover:ring-2 hover:ring-cobalt focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
            to="/plan"
          >
            Back to your plan
            <Icon as={ArrowRight} size="sm" />
          </Link>
        ) : (
          <p className="mt-2 text-sm text-muted">
            Type a craving above and your plan shows here, with its calories and macro split.
          </p>
        )}
      </section>

      {lists.status === 'ready' && (
        <section aria-labelledby="numbers-heading" className="rounded-3xl bg-surface p-5">
          <h2 className="font-display text-[20px] font-extrabold tracking-tight text-ink" id="numbers-heading">
            Your kitchen so far
          </h2>
          <dl className="mt-3 divide-y divide-dashed divide-line">
            {stats.map((stat) => (
              <div className="flex items-baseline justify-between gap-3 py-2.5" key={stat.label}>
                <dt className="text-sm text-muted">{stat.label}</dt>
                <dd className="font-mono text-[17px] font-bold tabular-nums text-ink">{stat.value}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}
    </aside>
  )
}

// Home (spec §4.2, layout B): the craving search with today's workout and
// dish cards, then this device's saved meals and past plans beside a context
// column. The welcome page makes the app's promises; a returning
// visitor is not shown them again.
function HomePage() {
  const planner = usePlannerContext()
  const lists = useMealLists(planner.userId, { enabled: planner.hasProfile })

  if (!planner.hasProfile) return <WelcomePage />

  return (
    <main>
      <CravingBanner />
      <div className={`${pageShell} grid gap-8 py-10 xl:grid-cols-[minmax(0,1fr)_340px] xl:items-start`}>
        <ContextColumn lists={lists} />
        <div className="flex min-w-0 flex-col gap-10">
        <section aria-labelledby="home-meals" className="flex flex-col gap-4">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className={sectionHeading} id="home-meals">
              <Icon as={Bookmark} size="lg" tone="light" />
              My meals
            </h2>
            <Link className="text-[15px] font-semibold underline-offset-4 hover:underline" to="/meals">
              See all
            </Link>
          </div>
          <MealGrid
            empty="Meals you save from a plan show up here."
            lists={lists}
            max={4}
            meals={lists.saved}
            showKey={false}
          />
        </section>
        <section aria-labelledby="home-history" className="flex flex-col gap-4">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className={sectionHeading} id="home-history">
              <Icon as={History} size="lg" tone="light" />
              Past plans
            </h2>
            <Link className="text-[15px] font-semibold underline-offset-4 hover:underline" to="/history">
              See all
            </Link>
          </div>
          <MealGrid empty="Plans you make show up here." lists={lists} max={4} meals={lists.history} showKey={false} />
        </section>
        </div>
      </div>
    </main>
  )
}

export default HomePage
