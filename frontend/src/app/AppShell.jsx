import { Bookmark, History, UserRound } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

import logoMark from '../assets/brand/logo-mark.svg'

const LINKS = [
  { to: '/meals', label: 'My meals', Icon: Bookmark },
  { to: '/history', label: 'Past plans', Icon: History },
  { to: '/profile', label: 'Profile', Icon: UserRound },
]

const linkClass = ({ isActive }) =>
  `flex min-h-[44px] items-center gap-2 rounded-xl px-3 text-[15px] font-medium text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-viridis-5 ${
    isActive ? 'bg-white/10' : 'hover:bg-white/10'
  }`

// The top bar on every page: the logo goes home, and three links with big
// icons and words (DESIGN.md §5: no tiles behind icons).
function AppShell() {
  return (
    <div className="min-h-screen bg-ground text-ink">
      <header className="bg-ink text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <NavLink
            className="flex min-h-[44px] items-center gap-2.5 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-viridis-5"
            to="/"
          >
            <img alt="" height="32" src={logoMark} width="32" />
            <span className="font-display text-xl font-extrabold">AI Meal Planner</span>
          </NavLink>
          <nav aria-label="Main" className="flex flex-wrap gap-1">
            {LINKS.map(({ to, label, Icon }) => (
              <NavLink className={linkClass} key={to} to={to}>
                <Icon aria-hidden="true" className="text-viridis-5" size={26} strokeWidth={1.8} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <Outlet />
    </div>
  )
}

export default AppShell
