import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import App from '../App'
import { saveStored } from '../app/storage'
import { DEFAULT_PROFILE } from '../features/profile/profile'

export const TEST_USER_ID = 'web-00000000-0000-4000-8000-000000000000'

// A returning visitor: the default details, already remembered.
export const STORED = { userId: TEST_USER_ID, profile: DEFAULT_PROFILE, location: 'Earlwood, NSW' }

// The whole app at a route. `stored` seeds this device's memory; without it
// the app opens on the first visit.
export function renderApp({ route = '/', stored = null } = {}) {
  localStorage.clear()
  if (stored) saveStored(stored)
  return render(
    <MemoryRouter initialEntries={[route]}>
      <App />
    </MemoryRouter>,
  )
}

export const cravingInput = () => screen.getByRole('textbox', { name: 'Your craving' })
export const planButton = () => screen.getByRole('button', { name: 'Plan my meal' })

// The first-visit form's button.
export const startButton = () => screen.getByRole('button', { name: 'Save and start planning' })

// Goes home by the logo, types a craving and plans.
export async function planMeal(user, craving = 'chicken fried rice') {
  const start = screen.queryByRole('button', { name: 'Save and start planning' })
  if (start) await user.click(start)
  if (!screen.queryByRole('textbox', { name: 'Your craving' })) await goHome(user)
  await user.clear(cravingInput())
  await user.type(cravingInput(), craving)
  await user.click(planButton())
}

export const goHome = (user) => user.click(screen.getByRole('link', { name: 'AI Meal Planner' }))
export const goToProfile = (user) => user.click(screen.getByRole('link', { name: 'Profile' }))

// From any page, back to the plan in memory by Home's link.
export async function backToPlan(user) {
  await goHome(user)
  await user.click(screen.getByRole('link', { name: /Back to your plan/ }))
}
