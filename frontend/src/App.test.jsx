import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'

import { STORAGE_KEY } from './app/storage'
import {
  STORED,
  cravingInput,
  goHome,
  goToProfile,
  planMeal,
  renderApp,
  startButton,
} from './test/renderApp'

// The app-level guarantees (DEC-29, kept through the kitchen-app redesign of
// 2026-11-22): no network on a first visit's first render, the request
// payload, the error and retry, the stale mark, and what is remembered.

const PLAN = {
  data: {
    request_id: 'req-00000001',
    plan_status: 'matched',
    meal_plan: {
      meal_definition: { structured_meal_name: 'Grilled Chicken Bowl', ingredients: [] },
    },
    nutrition: {},
    shopping_list: {},
  },
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('opens a first visit on the details form, with the brand and the main links', () => {
    renderApp()
    expect(screen.getByRole('link', { name: 'AI Meal Planner' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Tell us about you' })).toBeInTheDocument()
    const nav = screen.getByRole('navigation', { name: 'Main' })
    for (const name of ['Plan a meal', 'My meals', 'Past plans', 'Calories', 'Profile']) {
      expect(within(nav).getByRole('link', { name })).toBeInTheDocument()
    }
    expect(screen.queryByLabelText(/Your craving/i)).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Calorie Expenditure' })).not.toBeInTheDocument()
  })

  it('never calls the network on a first visit', () => {
    renderApp()
    expect(axios.get).not.toHaveBeenCalled()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('asks for nothing but the plan until the person plans', async () => {
    const user = userEvent.setup()
    renderApp()
    await user.click(startButton())
    expect(axios.post).not.toHaveBeenCalled()
    // Home loads this device's own lists, read-only.
    for (const [url] of axios.get.mock.calls) {
      expect(url).toMatch(/\/(saved-meals|meal-plans)\/web-[0-9a-f-]{36}$/)
    }
  })

  it('posts the craving, the profile and an opaque user ID to /generate-meal-plan', async () => {
    const user = userEvent.setup()
    renderApp()
    await user.click(startButton())
    await planMeal(user, 'High-protein burger')

    expect(axios.post).toHaveBeenCalledTimes(1)
    const [url, payload] = axios.post.mock.calls[0]
    expect(url).toEqual(expect.stringContaining('/generate-meal-plan'))
    expect(payload).toMatchObject({
      craving: 'High-protein burger',
      location: 'Earlwood, NSW',
      goal: 'maintain',
      age: 34,
      weight_kg: 64,
    })
    expect(payload.user_id).toMatch(/^web-[0-9a-f-]{36}$/)
  })

  it('opens the plan page and renders the returned plan', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await planMeal(user)

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Grilled Chicken Bowl' }),
    ).toHaveFocus()
  })

  it('shows the error and retries it', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Backend exploded' } } })
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await planMeal(user)

    const alert = await screen.findByRole('alert')
    expect(within(alert).getByText('Backend exploded')).toBeInTheDocument()
    await user.click(within(alert).getByRole('button', { name: 'Try again' }))
    expect(await screen.findByText('Grilled Chicken Bowl')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(axios.post).toHaveBeenCalledTimes(2)
  })

  // The stale-result guard, through the whole app.
  it('marks a plan stale after going back and changing the craving', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await planMeal(user, 'High-protein burger')
    await screen.findByText('Grilled Chicken Bowl')

    await user.click(screen.getByRole('button', { name: 'Try another craving' }))
    expect(cravingInput()).toHaveValue('High-protein burger')
    await user.type(cravingInput(), ' with fries')
    await user.click(screen.getByRole('link', { name: /Back to your plan/ }))

    expect(screen.getByRole('status')).toHaveTextContent('Made for your previous details.')
    expect(screen.getByText(/For your craving .High-protein burger./)).toBeInTheDocument()
  })

  it('keeps the profile, craving and plan across pages', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp()

    await user.clear(screen.getByLabelText('Weight (kg)'))
    await user.type(screen.getByLabelText('Weight (kg)'), '82')
    await user.click(screen.getByRole('checkbox', { name: 'Peanut allergy' }))
    await user.click(startButton())
    await planMeal(user, 'High-protein burger')
    await screen.findByText('Grilled Chicken Bowl')

    await goToProfile(user)
    expect(screen.getByLabelText('Weight (kg)')).toHaveValue(82)
    expect(screen.getByRole('checkbox', { name: 'Peanut allergy' })).toBeChecked()
    await goHome(user)
    expect(cravingInput()).toHaveValue('High-protein burger')
    expect(axios.post.mock.calls[0][1]).toMatchObject({
      weight_kg: 82,
      health_conditions: ['peanut allergy'],
    })
  })

  it('remembers only the user ID, profile and location, and no URL holds a detail', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp()
    await user.click(screen.getByRole('checkbox', { name: 'Kidney disease' }))
    await user.click(startButton())
    await planMeal(user)
    await screen.findByText('Grilled Chicken Bowl')

    expect(Object.keys(localStorage)).toEqual([STORAGE_KEY])
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY))
    expect(Object.keys(stored)).toEqual(['userId', 'profile', 'location'])
    expect(stored.profile.avoid).toEqual(['kidney'])
    for (const [url, options] of axios.get.mock.calls) {
      // The random user ID can contain "64" or "168", so only the rest of the URL is checked.
      expect(url.replace(stored.userId, '')).not.toMatch(/kidney|weight|age|64|168/i)
      expect(options?.params ?? {}).toEqual({ limit: 50 })
    }
  })

  it('shows who plans are sized for in the rail once there is a profile', () => {
    renderApp({ stored: STORED })
    const card = screen.getByRole('region', { name: 'Sized for you' })
    expect(card).toHaveTextContent('34 · Female · Maintain')
    expect(card).toHaveTextContent('Earlwood, NSW')
    expect(within(card).getByRole('link', { name: 'Edit details' })).toHaveAttribute('href', '/profile')
  })

  it('leaves the rail summary out on a first visit', () => {
    renderApp()
    expect(screen.queryByRole('region', { name: 'Sized for you' })).not.toBeInTheDocument()
  })

  it('opens the calorie estimate from its own tab, not from the profile page', async () => {
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await goToProfile(user)
    expect(screen.queryByRole('heading', { name: 'Calorie Expenditure' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: 'Calories' }))
    expect(screen.getByRole('heading', { name: 'Calorie Expenditure' })).toBeInTheDocument()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('forgets this device after a confirmation, back to the first visit', async () => {
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await goToProfile(user)

    await user.click(screen.getByRole('button', { name: 'Forget me on this device' }))
    expect(screen.getByText(/Plans already on the server are not deleted/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Keep my details' }))
    expect(localStorage.getItem(STORAGE_KEY)).not.toBeNull()

    await user.click(screen.getByRole('button', { name: 'Forget me on this device' }))
    await user.click(screen.getByRole('button', { name: 'Yes, forget me' }))
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull()
    expect(screen.getByRole('heading', { level: 2, name: 'Tell us about you' })).toBeInTheDocument()
  })

  it('opens a returning visit straight on the craving search', () => {
    renderApp({ stored: STORED })
    expect(screen.getByRole('heading', { level: 1, name: /Say what you crave/ })).toBeInTheDocument()
    expect(cravingInput()).toBeInTheDocument()
  })
})
