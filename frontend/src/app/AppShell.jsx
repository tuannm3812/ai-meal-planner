import Icon from '../components/icons/Icon'
import { Bookmark, Calculator, History, LogIn, UserRound, Utensils } from '../components/icons/glyphs'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'

import logoMark from '../assets/brand/logo-mark.svg'
import { GOAL_OPTIONS, SEX_OPTIONS } from '../features/profile/profile'
import { useAccount } from './AccountContext'
import { usePlannerContext } from './PlannerContext'

// `also` lists the pages that belong to a tab without sharing its path: the
// plan you just made is part of "Plan a meal", a stored plan part of "Past plans".
const LINKS = [
  { to: '/', label: 'Plan a meal', glyph: Utensils, end: true, also: ['/plan'] },
  { to: '/meals', label: 'My meals', glyph: Bookmark },
  { to: '/history', label: 'Past plans', glyph: History, also: ['/plans/'] },
  { to: '/calories', label: 'Calories', glyph: Calculator },
  { to: '/profile', label: 'Profile', glyph: UserRound },
]

// Below 1280 px the shell is an ink top bar; from 1280 px it is a white rail
// down the left (DEC-44), so wide screens use their full width. One nav
// element serves both, so there is a single "Main" landmark.
// Below 640 px the five tabs share one row, icon over label, so the bar stays
// one line tall instead of wrapping into three.
const linkClass = ({ isActive }) =>
  `flex min-h-[52px] flex-col items-center justify-center gap-1 rounded-xl px-1 text-center text-[11px] font-medium leading-tight focus:outline-none focus-visible:ring-2 focus-visible:ring-peach sm:min-h-[44px] sm:flex-row sm:gap-2.5 sm:px-3 sm:text-left sm:text-[15px] xl:min-h-[48px] xl:justify-start xl:focus-visible:ring-cobalt ${
    isActive
      ? 'bg-white/10 text-white xl:bg-ink xl:text-white'
      : 'text-white hover:bg-white/10 xl:text-ink xl:hover:bg-tint'
  }`

const isCurrent = (pathname, to, end) =>
  end ? pathname === to : pathname === to || pathname.startsWith(`${to}/`)

const inSection = (pathname, also = []) =>
  also.some((path) => (path.endsWith('/') ? pathname.startsWith(path) : pathname === path))

const iconClass = (isActive) => (isActive ? 'text-peach' : 'text-peach xl:text-cobalt')

const labelFor = (options, value) => options.find((option) => option.value === value)?.label

// Who the plans are sized for, at the foot of the rail (wide screens only).
function SizedFor() {
  const { hasProfile, profile, location, plan } = usePlannerContext()
  const target = plan?.macro_balance?.target_meal_calories
  if (!hasProfile) return null
  const details = [profile.age, labelFor(SEX_OPTIONS, profile.sex), labelFor(GOAL_OPTIONS, profile.goal)]
    .filter(Boolean)
    .join(' · ')
  return (
    <section
      aria-labelledby="sized-for-heading"
      className="mt-auto hidden rounded-2xl border border-ink bg-ground p-4 text-sm xl:block"
    >
      <h2 className="font-semibold text-ink" id="sized-for-heading">
        Sized for you
      </h2>
      <p className="mt-1 text-muted">{details}</p>
      {location && <p className="text-muted">{location}</p>}
      {typeof target === 'number' && <p className="text-muted">About {Math.round(target)} kcal a meal</p>}
      <Link
        className="mt-2 inline-flex min-h-[44px] items-center font-semibold text-cobalt underline underline-offset-4 focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt"
        to="/profile"
      >
        Edit details
      </Link>
    </section>
  )
}

function AppShell() {
  const account = useAccount()
  const { pathname } = useLocation()
  return (
    <div className="min-h-screen bg-ground text-ink xl:grid xl:grid-cols-[256px_minmax(0,1fr)]">
      <header className="bg-ink text-white xl:sticky xl:top-0 xl:h-screen xl:overflow-y-auto xl:border-r xl:border-line xl:bg-surface xl:text-ink">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 xl:h-full xl:max-w-none xl:flex-col xl:flex-nowrap xl:items-stretch xl:justify-start xl:gap-8 xl:px-4 xl:py-6">
          <NavLink
            className="flex min-h-[44px] items-center gap-2.5 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-peach xl:px-2 xl:focus-visible:ring-cobalt"
            to="/"
          >
            <img alt="" height="32" src={logoMark} width="32" />
            <span className="whitespace-nowrap font-display text-lg font-extrabold xl:text-[17px]">AI Meal Planner</span>
          </NavLink>
          <nav
            aria-label="Main"
            className="grid w-full auto-cols-fr grid-flow-col gap-1 sm:flex sm:w-auto sm:flex-wrap xl:flex-col xl:gap-1.5"
          >
            {LINKS.map(({ to, label, glyph, end, also }) => {
              const active = isCurrent(pathname, to, end) || inSection(pathname, also)
              return (
                <Link
                  aria-current={active ? 'page' : undefined}
                  className={linkClass({ isActive: active })}
                  key={to}
                  to={to}
                >
                  <Icon as={glyph} className={iconClass(active)} />
                  {label}
                </Link>
              )
            })}
            {account.enabled && !account.signedIn && (
              <button
                className={linkClass({ isActive: false })}
                disabled={account.busy}
                onClick={account.signIn}
                type="button"
              >
                <Icon as={LogIn} className={iconClass(false)} />
                Sign in
              </button>
            )}
          </nav>
          <SizedFor />
        </div>
      </header>
      <div className="min-w-0">
        <Outlet />
      </div>
    </div>
  )
}

export default AppShell
