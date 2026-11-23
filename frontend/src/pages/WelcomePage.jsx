import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import {
  ArrowRight,
  BookOpenCheck,
  Check,
  MessageSquareText,
  PieChart,
  Search,
  ShoppingBasket,
  UserRound,
} from '../components/icons/glyphs'
import BlobShape from '../components/illustrations/BlobShape'
import DishIllustration from '../components/illustrations/DishIllustration'
import { ghostButton, pageShell, primaryButton } from '../components/ui/styles'
import { CRAVING_SUGGESTIONS } from '../features/craving/craving'
import LocationField from '../features/profile/LocationField'
import ProfileForm from '../features/profile/ProfileForm'
import { PROFILE_DISCLOSURE } from '../features/profile/profile'

// The first visit (spec §4.1) as a landing page: what the app does in a few
// short sections, then the details every meal is sized from. Nothing is sent
// until the person plans a meal.

// Every claim here is true today: anonymous use needs no sign-up, and the
// example plan is a real service response (docs/8_design.md §2).
const HERO_POINTS = ['Free to use', 'No sign-up needed', 'Set up in a minute']

// The corpus size; WelcomePage.test.jsx checks it against data/meal_corpus.
const MENU_SIZE = 76

const STEPS = [
  { glyph: UserRound, title: 'Tell us about you', body: 'Your body, goal and activity, once.' },
  { glyph: Search, title: 'Say what you crave', body: 'Type it the way you would say it.' },
  { glyph: ShoppingBasket, title: 'Cook and shop', body: 'One meal sized for you, plus the shopping list.' },
]

// No claim that a standard (fallback) meal is balanced or a good match.
const PROMISES = [
  { glyph: BookOpenCheck, title: 'Tested recipes', body: 'Every meal comes from a real menu, never made up.' },
  {
    glyph: PieChart,
    title: 'Portions that fit',
    body: 'Sized to your calories, and the plan says if the macros landed in range.',
  },
  {
    glyph: MessageSquareText,
    title: 'Honest when it misses',
    body: 'No close match? You get a standard meal and a note saying so.',
  },
]

function Hero() {
  return (
    <section aria-labelledby="welcome-heading" className="relative overflow-hidden bg-ink text-white">
      <div className={`${pageShell} grid items-center gap-10 pb-16 pt-12 md:grid-cols-[1.15fr_1fr] md:pb-24 md:pt-20`}>
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
            <a className={`${primaryButton} min-h-[60px] px-8 text-lg`} href="#get-started">
              Get started
              <Icon as={ArrowRight} size="sm" />
            </a>
            <a className={`${ghostButton} min-h-[60px] px-7 text-lg`} href="#how-it-works">
              How it works
            </a>
          </div>
          <ul className="flex flex-wrap gap-x-6 gap-y-2 text-[15px] text-on-ink-muted">
            {HERO_POINTS.map((point) => (
              <li className="flex items-center gap-2" key={point}>
                <Icon as={Check} size="sm" tone="ink" />
                {point}
              </li>
            ))}
          </ul>
        </div>

        <div aria-hidden="true" className="relative mx-auto w-full max-w-[460px]">
          <BlobShape className="absolute -left-6 -top-10 w-[115%]" />
          <DishIllustration className="relative w-full -translate-y-6" type="rice" />
          <div className="absolute -bottom-12 left-0 rounded-3xl bg-surface p-4 text-ink sm:-left-10 sm:p-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted">Example plan</p>
            <p className="mt-1 font-display text-lg font-extrabold sm:text-xl">Chicken Fried Rice</p>
            <p className="mt-1 flex items-baseline gap-2">
              <span className="font-display text-2xl font-extrabold sm:text-3xl">629 kcal</span>
              <span className="text-sm text-muted">target 625</span>
            </p>
            <span className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-success-bg px-3 py-1 text-sm font-semibold text-success-fg">
              <Icon as={Check} size="sm" />
              On target
            </span>
          </div>
          <div className="absolute -right-2 top-2 flex items-center gap-2 rounded-full bg-surface px-4 py-2.5 text-sm font-semibold text-ink sm:right-0">
            <Icon as={ShoppingBasket} size="sm" tone="light" />
            Shopping list ready
          </div>
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
              <p className="text-sm font-semibold uppercase tracking-wider text-accent-text">
                Step {index + 1}
              </p>
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
    <section aria-labelledby="menu-heading" className="bg-tint py-16 sm:py-20">
      <div className={pageShell}>
        <div>
            <h2 className="font-display text-4xl font-extrabold tracking-tight text-ink" id="menu-heading">
              A real menu, not made-up meals
            </h2>
            <p className="mt-2 text-lg text-muted">
              {MENU_SIZE} tested recipes. Here are a few to try.
            </p>
        </div>
        <ul className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {CRAVING_SUGGESTIONS.map(({ meal }) => (
            <li className="flex flex-col items-center gap-3 rounded-3xl bg-surface p-4 text-center" key={meal}>
              <DishIllustration className="w-full" mealName={meal} />
              <p className="font-semibold leading-snug text-ink">{meal}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

function Promises() {
  return (
    <section aria-labelledby="promises-heading" className="bg-ink py-16 text-white sm:py-20">
      <div className={pageShell}>
        <h2 className="font-display text-4xl font-extrabold tracking-tight" id="promises-heading">
          Built to be trusted
        </h2>
        <ul className="mt-10 grid gap-10 sm:grid-cols-3">
          {PROMISES.map(({ glyph, title, body }) => (
            <li className="flex flex-col gap-3" key={title}>
              <Icon as={glyph} size="xl" tone="ink" />
              <p className="font-display text-2xl font-extrabold tracking-tight">{title}</p>
              <p className="text-on-ink-muted">{body}</p>
            </li>
          ))}
        </ul>
        <p className="mt-12 border-t border-white/15 pt-5 text-sm text-on-ink-muted">
          A planning aid, not medical advice.
        </p>
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
    <section className="scroll-mt-4 py-16 sm:py-20" id="get-started">
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
          <button className={`${primaryButton} min-h-[60px] px-8 text-lg`} disabled={!profileIsValid || !locationOk} type="submit">
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

function WelcomePage() {
  return (
    <main>
      <Hero />
      <HowItWorks />
      <Menu />
      <Promises />
      <GetStarted />
    </main>
  )
}

export default WelcomePage
