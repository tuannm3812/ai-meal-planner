import { Link, useNavigate } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import {
  ArrowRight,
  BookOpenCheck,
  Bookmark,
  History,
  MessageSquareText,
  Search,
  ShoppingBasket,
} from '../components/icons/glyphs'
import BlobShape from '../components/illustrations/BlobShape'
import DishIllustration from '../components/illustrations/DishIllustration'
import { pageShell, primaryButton, sectionHeading } from '../components/ui/styles'
import { CRAVING_SUGGESTIONS } from '../features/craving/craving'
import MealGrid from '../features/meals/MealGrid'
import { useMealLists } from '../features/meals/useMealLists'
import LocationField from '../features/profile/LocationField'
import ProfileForm from '../features/profile/ProfileForm'

// The first visit (spec §4.1): the details every meal is sized from, then the
// normal home page. Nothing is sent until the person plans a meal.
function Welcome() {
  const planner = usePlannerContext()
  const { profile, setProfile, fieldErrors, profileIsValid, location, setLocation, requestFieldErrors } =
    planner
  const locationOk = !requestFieldErrors.location

  const start = (event) => {
    event.preventDefault()
    if (profileIsValid && locationOk) planner.confirmProfile()
  }

  return (
    <main>
      <section className="bg-ink text-white">
        <div className={`${pageShell} py-10`}>
          <p className="text-[15px] font-semibold text-lime">Welcome</p>
          <p className="mt-2 max-w-3xl font-display text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
            Say what you crave. Get a meal that fits you.
          </p>
          <p className="mt-3 max-w-2xl text-on-ink-muted">
            First, a few details so every meal is sized for you. You only do this once on this
            device.
          </p>
        </div>
      </section>
      <form className={`${pageShell} flex flex-col gap-6 py-8`} noValidate onSubmit={start}>
        <ProfileForm errors={fieldErrors} onChange={setProfile} profile={profile}>
          <LocationField error={requestFieldErrors.location} onChange={setLocation} value={location} />
        </ProfileForm>
        <div className="flex flex-wrap items-center gap-4">
          <button className={primaryButton} disabled={!profileIsValid || !locationOk} type="submit">
            Save and start planning
          </button>
          <span className="text-sm text-muted">
            {profileIsValid && locationOk
              ? 'You can change these at any time on your profile.'
              : 'Fix the highlighted details to continue.'}
          </span>
        </div>
      </form>
    </main>
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
    <section aria-labelledby="home-heading" className="relative overflow-hidden bg-ink text-white">
      <div className={`${pageShell} relative flex flex-wrap items-center gap-8 pb-16 pt-10`}>
        <div className="flex min-w-0 flex-[3_1_480px] flex-col gap-5">
          <h1
            className="font-display text-4xl font-extrabold leading-[1.02] tracking-tight sm:text-[58px]"
            id="home-heading"
          >
            Say what you crave. <span className="text-lime">Get a meal that fits you.</span>
          </h1>
          <form className="flex flex-col gap-3" noValidate onSubmit={submit}>
            <div className="flex flex-wrap gap-3">
              <div className="flex min-h-[64px] flex-[1_1_320px] items-center gap-3 rounded-2xl bg-surface px-5 text-ink focus-within:ring-2 focus-within:ring-lime">
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
          <div>
            <p className="text-sm text-on-ink-muted" id="craving-suggestions">
              Or try one of these
            </p>
            <ul aria-labelledby="craving-suggestions" className="mt-2 flex flex-wrap gap-2">
              {CRAVING_SUGGESTIONS.map((suggestion) => (
                <li key={suggestion.meal}>
                  <button
                    className="min-h-[44px] rounded-full border border-white/40 px-4 text-sm text-white hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-lime"
                    onClick={() => setCraving(suggestion.label.toLowerCase())}
                    type="button"
                  >
                    {suggestion.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <p className="text-sm text-on-ink-muted">
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
    </section>
  )
}

// Three promises, each true today: no claim that the standard meal is
// balanced or a good match.
const PROMISES = [
  {
    title: 'Matched to a real menu',
    body: 'Every meal comes from a tested recipe, never made up on the spot.',
    glyph: BookOpenCheck,
  },
  {
    title: 'Honest when it misses',
    body: 'No close match? You get a standard meal and a note saying so.',
    glyph: MessageSquareText,
  },
  {
    title: 'Shopping list included',
    body: 'Ingredients mapped to store aisles, with estimated prices.',
    glyph: ShoppingBasket,
  },
]

// Home (spec §4.2, layout B): the craving search, then this device's saved
// meals and past plans.
function HomePage() {
  const planner = usePlannerContext()
  const lists = useMealLists(planner.userId, { enabled: planner.hasProfile })

  if (!planner.hasProfile) return <Welcome />

  return (
    <main>
      <CravingBanner />
      <div className={`${pageShell} flex flex-col gap-10 py-10`}>
        {planner.submitted && (
          <Link
            className="flex min-h-[56px] items-center justify-between gap-3 rounded-2xl bg-tint px-5 font-semibold text-ink hover:ring-2 hover:ring-leaf focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
            to="/plan"
          >
            <span>
              Back to your plan
              {planner.plan?.meal_plan?.meal_definition?.structured_meal_name &&
                `: ${planner.plan.meal_plan.meal_definition.structured_meal_name}`}
            </span>
            <Icon as={ArrowRight} size="sm" />
          </Link>
        )}
        <ul className="grid gap-5 sm:grid-cols-3">
          {PROMISES.map(({ title, body, glyph }) => (
            <li className="flex gap-4" key={title}>
              <Icon as={glyph} size="lg" tone="light" />
              <div>
                <p className="font-semibold text-ink">{title}</p>
                <p className="mt-0.5 text-sm text-muted">{body}</p>
              </div>
            </li>
          ))}
        </ul>
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
          <MealGrid empty="Plans you make show up here." lists={lists} max={4} meals={lists.history} />
        </section>
      </div>
    </main>
  )
}

export default HomePage
