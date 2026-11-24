import { usePlannerContext } from '../app/PlannerContext'
import logoMark from '../assets/brand/logo-mark.svg'
import Icon from '../components/icons/Icon'
import {
  ArrowRight,
  CircleCheck,
  Flame,
  MessageSquareText,
  Search,
  ShoppingBasket,
  Timer,
  UserRound,
} from '../components/icons/glyphs'
import BlobShape from '../components/illustrations/BlobShape'
import DishIllustration from '../components/illustrations/DishIllustration'
import Note from '../components/ui/Note'
import { ghostButton, pageShell, primaryButton, secondaryButton } from '../components/ui/styles'
import { CRAVING_SUGGESTIONS } from '../features/craving/craving'
import CalorieRing from '../features/plan/charts/CalorieRing'
import MacroDonut from '../features/plan/charts/MacroDonut'
import { MACROS } from '../features/plan/plan'
import LocationField from '../features/profile/LocationField'
import ProfileForm from '../features/profile/ProfileForm'
import { PROFILE_DISCLOSURE } from '../features/profile/profile'

// The first visit (spec §4.1) as a landing page: what the app does in a few
// short sections, then the details every meal is sized from. Nothing is sent
// until the person plans a meal.

// The example is a real service response (features/plan/samplePlan.js and
// docs/8_design.md §2: "chicken fried rice" for a 34-year-old woman
// maintaining her weight), rounded, and labelled as an example wherever it shows.
const EXAMPLE = {
  meal: 'Chicken Fried Rice',
  kcal: 629,
  target: 625,
  split: { protein: 27, carbs: 46, fat: 27 },
  grams: { protein: 42, carbs: 71, fat: 18 },
  shopping: '$24.50',
}

// The corpus size; WelcomePage.test.jsx checks it against data/meal_corpus.
const MENU_SIZE = 76

const STEPS = [
  { glyph: UserRound, title: 'Tell us about you', body: 'Your body, goal and activity, once.' },
  { glyph: Search, title: 'Say what you crave', body: 'Type it the way you would say it.' },
  { glyph: ShoppingBasket, title: 'Cook and shop', body: 'Get the meal and its shopping list.' },
]

// No claim that a standard (fallback) meal is balanced or a good match.
const CHECKS = [
  { glyph: Flame, text: 'Calories against your own target' },
  { glyph: CircleCheck, text: 'Says whether protein, carbs and fat landed in range' },
  { glyph: MessageSquareText, text: 'An honest note when nothing on the menu is close' },
]

// Scroll to a section without changing the URL: the first visit never
// touches history (ProfileStep.test.jsx).
function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
}

function goToForm() {
  const heading = document.getElementById('profile-heading')
  heading?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  heading?.focus({ preventScroll: true })
}

function FloatingChip({ className = '', children }) {
  return (
    <div className={`absolute flex items-center gap-3 rounded-2xl bg-surface px-4 py-3 text-ink shadow-2xl ${className}`}>
      {children}
    </div>
  )
}

function Hero() {
  return (
    <section aria-labelledby="welcome-heading" className="relative overflow-hidden bg-cobalt text-white">
      <div className={`${pageShell} grid grid-cols-[minmax(0,1fr)] items-center gap-12 pb-28 pt-12 lg:grid-cols-[1.1fr_1fr] lg:pb-32 lg:pt-16`}>
        <div className="flex flex-col gap-6">
          <p className="w-fit rounded-full border border-white/25 px-4 py-1.5 text-sm font-semibold text-peach">
            One meal at a time
          </p>
          <h1
            className="font-display text-[44px] font-extrabold leading-[1.02] tracking-tight sm:text-[64px]"
            id="welcome-heading"
          >
            Say what you crave. <span className="text-peach">Get a meal that fits you.</span>
          </h1>
          <p className="max-w-xl text-lg leading-8 text-on-ink-muted">
            One tested recipe, sized to your body and goal, with a shopping list to match.
          </p>
          <div className="flex flex-wrap gap-3">
            <button className={`${primaryButton} min-h-[60px] px-8 text-lg`} onClick={goToForm} type="button">
              Get started
              <Icon as={ArrowRight} size="sm" />
            </button>
            <button
              className={`${ghostButton} min-h-[60px] px-7 text-lg`}
              onClick={() => scrollTo('example')}
              type="button"
            >
              See an example plan
            </button>
          </div>
          <p className="flex items-center gap-2 text-[15px] text-on-ink-muted">
            <Icon as={Timer} size="sm" tone="ink" />
            Free, no sign-up, set up in a minute.
          </p>
        </div>

        <div aria-hidden="true" className="relative mx-auto hidden h-[440px] w-full max-w-[480px] sm:block">
          <BlobShape className="absolute inset-0 m-auto w-[460px]" />
          <DishIllustration className="absolute inset-x-0 top-[90px] mx-auto w-[400px]" type="rice" />
          <FloatingChip className="left-0 top-6">
            <Icon as={Flame} size="lg" tone="light" />
            <span>
              <span className="block font-display text-2xl font-extrabold leading-none">{EXAMPLE.kcal} kcal</span>
              <span className="text-sm text-muted">of a {EXAMPLE.target} kcal target</span>
            </span>
          </FloatingChip>
          <FloatingChip className="right-0 top-[150px]">
            <Icon as={ShoppingBasket} size="lg" tone="light" />
            <span>
              <span className="block font-display text-2xl font-extrabold leading-none">{EXAMPLE.shopping}</span>
              <span className="text-sm text-muted">shopping list</span>
            </span>
          </FloatingChip>
          <FloatingChip className="bottom-2 left-6 flex-col !items-start gap-2">
            <span className="text-sm font-semibold">Example plan · macro split</span>
            <span className="flex h-3 w-[220px] overflow-hidden rounded-full">
              {MACROS.map((macro) => (
                <span className={macro.bar} key={macro.key} style={{ width: `${EXAMPLE.split[macro.key]}%` }} />
              ))}
            </span>
            <span className="flex gap-3 text-xs text-muted">
              {MACROS.map((macro) => (
                <span key={macro.key}>
                  {macro.label} {EXAMPLE.split[macro.key]}%
                </span>
              ))}
            </span>
          </FloatingChip>
        </div>
      </div>
    </section>
  )
}

// Three steps in one strip that sits over the hero's lower edge, so the form
// comes straight after it.
function HowItWorks() {
  return (
    <section aria-labelledby="how-heading" className="relative -mt-20 scroll-mt-4" id="how-it-works">
      <div className={pageShell}>
        <div className="grid gap-x-10 gap-y-6 rounded-3xl border border-ink bg-surface p-6 sm:p-8 lg:grid-cols-[180px_minmax(0,1fr)] lg:items-center">
          <h2 className="font-display text-2xl font-extrabold leading-tight tracking-tight text-ink" id="how-heading">
            How it works
          </h2>
          <ol className="grid gap-6 sm:grid-cols-3">
            {STEPS.map(({ glyph, title, body }, index) => (
              <li className="flex items-start gap-3.5" key={title}>
                <Icon as={glyph} size="lg" tone="light" />
                <div className="min-w-0">
                  <p className="text-xs font-semibold uppercase tracking-wider text-accent-text">Step {index + 1}</p>
                  <p className="mt-0.5 font-semibold leading-6 text-ink">{title}</p>
                  <p className="mt-0.5 text-sm leading-5 text-muted">{body}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  )
}

function Menu() {
  return (
    <section aria-labelledby="menu-heading" className="bg-surface py-14 sm:py-16">
      <div className={pageShell}>
        <h2 className="font-display text-3xl font-extrabold tracking-tight text-ink sm:text-4xl" id="menu-heading">
          A real menu, not made-up meals
        </h2>
        <p className="mt-3 text-lg text-muted">{MENU_SIZE} tested recipes. Here are a few to try.</p>
        <ul className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {CRAVING_SUGGESTIONS.map(({ meal }) => (
            <li className="flex flex-col items-center gap-3 rounded-3xl bg-ground p-4 text-center" key={meal}>
              <DishIllustration className="w-full" mealName={meal} />
              <p className="font-semibold leading-snug text-ink">{meal}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

function ExamplePlan() {
  return (
    <section aria-labelledby="example-heading" className="scroll-mt-4 bg-tint" id="example">
      <div className={`${pageShell} grid grid-cols-[minmax(0,1fr)] items-center gap-12 py-14 sm:py-16 lg:grid-cols-[1fr_1.1fr]`}>
        <div>
          <h2 className="font-display text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl" id="example-heading">
            Every plan shows its working
          </h2>
          <ul className="mt-8 flex flex-col gap-5">
            {CHECKS.map((check) => (
              <li className="flex items-start gap-4 text-lg leading-8 text-ink" key={check.text}>
                <Icon as={check.glyph} size="lg" tone="light" />
                {check.text}
              </li>
            ))}
          </ul>
          <button className={`${secondaryButton} mt-8`} onClick={goToForm} type="button">
            Fill in my details
            <Icon as={ArrowRight} size="sm" />
          </button>
        </div>

        <figure className="m-0 rounded-3xl border border-ink bg-surface p-5 sm:p-7">
          <figcaption className="flex items-center gap-4">
            <DishIllustration className="w-24 shrink-0" type="rice" />
            <span>
              <span className="block text-sm font-semibold uppercase tracking-wider text-muted">Example plan</span>
              <span className="block font-display text-3xl font-extrabold text-ink">{EXAMPLE.meal}</span>
            </span>
          </figcaption>
          <div className="mt-6 flex flex-wrap items-center gap-x-10 gap-y-6 border-t border-line pt-6">
            <CalorieRing target={EXAMPLE.target} total={EXAMPLE.kcal} />
            <MacroDonut grams={EXAMPLE.grams} split={EXAMPLE.split} />
          </div>
          <p className="mt-6 flex items-center gap-3 rounded-2xl bg-ground px-4 py-3 text-ink">
            <Icon as={ShoppingBasket} tone="light" />
            Shopping list, about {EXAMPLE.shopping}, sorted by aisle
          </p>
        </figure>
      </div>
    </section>
  )
}

function GetStarted() {
  const planner = usePlannerContext()
  const { profile, setProfile, fieldErrors, profileIsValid, location, setLocation, requestFieldErrors } =
    planner
  const locationOk = !requestFieldErrors.location
  const ready = profileIsValid && locationOk

  const start = (event) => {
    event.preventDefault()
    if (ready) planner.confirmProfile()
  }

  return (
    <section aria-label="Get started" className="scroll-mt-4 py-12 sm:py-14" id="get-started">
      <form className={pageShell} noValidate onSubmit={start}>
        <ProfileForm
          badge="About a minute"
          errors={fieldErrors}
          eyebrow="Get started"
          footer={
            <div className="flex flex-col gap-5">
              <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
                <button
                  className={`${primaryButton} min-h-[60px] px-8 text-lg`}
                  disabled={!ready}
                  type="submit"
                >
                  Save and start planning
                  <Icon as={ArrowRight} size="sm" />
                </button>
                <span className={`text-sm ${ready ? 'text-muted' : 'font-medium text-danger-fg'}`}>
                  {ready
                    ? 'You can change these at any time on your profile.'
                    : 'Fix the highlighted details to continue.'}
                </span>
              </div>
              <Note className="max-w-3xl" onGround>{PROFILE_DISCLOSURE}</Note>
            </div>
          }
          headingLevel={2}
          intro="A few details so every meal is sized for you. You only do this once on this device."
          onChange={setProfile}
          profile={profile}
          showSizing={false}
        >
          <LocationField error={requestFieldErrors.location} onChange={setLocation} value={location} />
        </ProfileForm>
      </form>
    </section>
  )
}

function Footer() {
  return (
    <footer className="bg-ink text-white">
      <div className={`${pageShell} flex flex-wrap items-center justify-between gap-4 py-10`}>
        <span className="flex items-center gap-2.5">
          <img alt="" height="28" src={logoMark} width="28" />
          <span className="font-display text-lg font-extrabold">AI Meal Planner</span>
        </span>
        <span className="text-sm text-on-ink-muted">A planning aid, not medical advice.</span>
      </div>
    </footer>
  )
}

function WelcomePage() {
  return (
    <>
      <main>
        <Hero />
        <HowItWorks />
        <GetStarted />
        <Menu />
        <ExamplePlan />
      </main>
      <Footer />
    </>
  )
}

export default WelcomePage
