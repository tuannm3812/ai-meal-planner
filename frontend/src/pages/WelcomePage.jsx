import { usePlannerContext } from '../app/PlannerContext'
import logoMark from '../assets/brand/logo-mark.svg'
import Icon from '../components/icons/Icon'
import {
  ArrowRight,
  BookOpenCheck,
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
import { ghostButton, pageShell, primaryButton } from '../components/ui/styles'
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
  { glyph: ShoppingBasket, title: 'Cook and shop', body: 'One meal sized for you, plus the shopping list.' },
]

// No claim that a standard (fallback) meal is balanced or a good match.
const CHECKS = [
  { glyph: Flame, text: 'Calories sized to your body and goal' },
  { glyph: CircleCheck, text: 'Says whether protein, carbs and fat landed in range' },
  { glyph: BookOpenCheck, text: 'Every meal from a tested recipe, never made up' },
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
    <section aria-labelledby="welcome-heading" className="relative overflow-hidden bg-ink text-white">
      <div className={`${pageShell} grid grid-cols-[minmax(0,1fr)] items-center gap-12 py-14 lg:grid-cols-[1.1fr_1fr] lg:py-24`}>
        <div className="flex flex-col gap-6">
          <p className="w-fit rounded-full border border-white/25 px-4 py-1.5 text-sm font-semibold text-lime">
            Meal planning, sized to you
          </p>
          <h1
            className="font-display text-[44px] font-extrabold leading-[1.02] tracking-tight sm:text-[64px]"
            id="welcome-heading"
          >
            Say what you crave. <span className="text-lime">Get a meal that fits you.</span>
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
              onClick={() => scrollTo('how-it-works')}
              type="button"
            >
              How it works
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

function HowItWorks() {
  return (
    <section aria-labelledby="how-heading" className="scroll-mt-4 py-16 sm:py-20" id="how-it-works">
      <div className={pageShell}>
        <h2 className="text-center font-display text-4xl font-extrabold tracking-tight text-ink" id="how-heading">
          How it works
        </h2>
        <ol className="mt-12 grid gap-10 sm:grid-cols-3">
          {STEPS.map(({ glyph, title, body }, index) => (
            <li className="flex flex-col items-center gap-3 text-center" key={title}>
              <Icon as={glyph} size="xl" tone="light" />
              <p className="text-sm font-semibold uppercase tracking-wider text-accent-text">Step {index + 1}</p>
              <p className="font-display text-2xl font-extrabold tracking-tight text-ink">{title}</p>
              <p className="max-w-xs text-muted">{body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}

function Menu() {
  return (
    <section aria-labelledby="menu-heading" className="bg-surface py-16 sm:py-20">
      <div className={pageShell}>
        <h2 className="font-display text-4xl font-extrabold tracking-tight text-ink" id="menu-heading">
          A real menu, not made-up meals
        </h2>
        <p className="mt-2 text-lg text-muted">{MENU_SIZE} tested recipes. Here are a few to try.</p>
        <ul className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
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
    <section aria-labelledby="example-heading" className="bg-tint">
      <div className={`${pageShell} grid grid-cols-[minmax(0,1fr)] items-center gap-12 py-16 sm:py-20 lg:grid-cols-[1fr_1.1fr]`}>
        <div>
          <h2 className="font-display text-4xl font-extrabold leading-tight tracking-tight text-ink" id="example-heading">
            Every plan shows its working
          </h2>
          <ul className="mt-8 flex flex-col gap-5">
            {CHECKS.map((check) => (
              <li className="flex items-center gap-4 text-lg text-ink" key={check.text}>
                <Icon as={check.glyph} size="lg" tone="light" />
                {check.text}
              </li>
            ))}
          </ul>
        </div>

        <figure className="m-0 rounded-3xl bg-surface p-5 shadow-xl sm:p-7">
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

  const start = (event) => {
    event.preventDefault()
    if (profileIsValid && locationOk) planner.confirmProfile()
  }

  return (
    <section aria-label="Get started" className="scroll-mt-4 py-16 sm:py-20" id="get-started">
      <form className={`${pageShell} flex flex-col gap-6`} noValidate onSubmit={start}>
        <ProfileForm
          errors={fieldErrors}
          eyebrow="Get started"
          headingLevel={2}
          intro="A few details so every meal is sized for you. You only do this once on this device."
          onChange={setProfile}
          profile={profile}
          showSizing={false}
        >
          <LocationField error={requestFieldErrors.location} onChange={setLocation} value={location} />
        </ProfileForm>
        <div className="flex flex-wrap items-center gap-4">
          <button
            className={`${primaryButton} min-h-[60px] px-8 text-lg`}
            disabled={!profileIsValid || !locationOk}
            type="submit"
          >
            Save and start planning
          </button>
          <span className="text-sm text-muted">
            {profileIsValid && locationOk
              ? 'You can change these at any time on your profile.'
              : 'Fix the highlighted details to continue.'}
          </span>
        </div>
        <p className="max-w-3xl text-sm leading-6 text-muted">{PROFILE_DISCLOSURE}</p>
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
        <Menu />
        <ExamplePlan />
        <GetStarted />
      </main>
      <Footer />
    </>
  )
}

export default WelcomePage
