import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'
import App from './App'

// The flow tests that replace the three-tab App.test.jsx (DEC-29). Each
// guarantee the old file held is kept here or in the test named next to it;
// docs/5_agent_log.md lists the mapping.

const PLAN = {
  data: {
    request_id: 'req-1',
    plan_status: 'matched',
    meal_plan: {
      meal_definition: { structured_meal_name: 'Grilled Chicken Bowl', ingredients: [] },
    },
    nutrition: {},
    shopping_list: {},
  },
}

const next = () => screen.getByRole('button', { name: 'Next: what are you craving?' })
const cravingInput = () => screen.getByLabelText(/Your craving/i)
const planButton = () => screen.getByRole('button', { name: 'Plan my meal' })

async function planFromStart(user, craving = 'High-protein burger') {
  await user.click(next())
  await user.type(cravingInput(), craving)
  await user.click(planButton())
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Old: "renders without crashing and shows the tab bar" and "shows the meal
  // plan tab content by default".
  it('opens on step 1 of the flow, with the brand and the step indicator', () => {
    render(<App />)
    expect(screen.getByText('AI Meal Planner')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1, name: 'Tell us about you' })).toBeInTheDocument()
    const progress = screen.getByRole('navigation', { name: 'Progress' })
    expect(within(progress).getByRole('button', { name: '1 · You' })).toHaveAttribute(
      'aria-current',
      'step',
    )
    // The plan step cannot be opened before a plan has been asked for.
    expect(within(progress).getByRole('button', { name: '3 · Your plan' })).toBeDisabled()
    expect(screen.queryByRole('button', { name: 'Meal Plan' })).not.toBeInTheDocument()
  })

  // Old: "never calls the network on first render". Kept as it was.
  it('never calls the network on first render', () => {
    render(<App />)
    expect(axios.get).not.toHaveBeenCalled()
    expect(axios.post).not.toHaveBeenCalled()
  })

  // Old: "fires axios.post to /generate-meal-plan when the meal plan form is
  // submitted". The exact payload is pinned in ProfileStep.test.jsx ("sends
  // the profile with the meal request").
  it('posts the craving, the profile and an opaque user ID to /generate-meal-plan', async () => {
    const user = userEvent.setup()
    render(<App />)
    await planFromStart(user)

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

  // Old: "renders part of the returned plan when axios.post resolves".
  it('moves to the plan step and renders the returned plan', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<App />)
    await planFromStart(user)

    expect(await screen.findByText('Grilled Chicken Bowl')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1, name: 'Your plan' })).toHaveFocus()
  })

  // Old: "renders the error banner when axios.post rejects". Error and retry
  // per status are in PlanScreen.test.jsx ("Plan screen failures").
  it('shows the error and retries it', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Backend exploded' } } })
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<App />)
    await planFromStart(user)

    const alert = await screen.findByRole('alert')
    expect(within(alert).getByText('Backend exploded')).toBeInTheDocument()
    await user.click(within(alert).getByRole('button', { name: 'Try again' }))
    expect(await screen.findByText('Grilled Chicken Bowl')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(axios.post).toHaveBeenCalledTimes(2)
  })

  // The stale-result guard, through the whole app. In-flight drops are in
  // CravingStep.test.jsx; the submitted-craving label in MealFlow.test.jsx.
  it('marks a plan stale after going back and changing the craving', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<App />)
    await planFromStart(user)
    await screen.findByText('Grilled Chicken Bowl')

    await user.click(screen.getByRole('button', { name: 'Try another craving' }))
    expect(screen.getByRole('heading', { name: 'What are you in the mood for?' })).toHaveFocus()
    expect(cravingInput()).toHaveValue('High-protein burger')
    await user.type(cravingInput(), ' with fries')
    await user.click(screen.getByRole('button', { name: '3 · Your plan' }))

    expect(screen.getByRole('status')).toHaveTextContent('Made for your previous details.')
    expect(screen.getByText(/For your craving .High-protein burger./)).toBeInTheDocument()
  })

  it('keeps the profile, craving and plan across the step indicator', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<App />)

    await user.clear(screen.getByLabelText('Weight (kg)'))
    await user.type(screen.getByLabelText('Weight (kg)'), '82')
    await user.click(screen.getByRole('checkbox', { name: 'Peanut allergy' }))
    await planFromStart(user)
    await screen.findByText('Grilled Chicken Bowl')

    await user.click(screen.getByRole('button', { name: '1 · You' }))
    expect(screen.getByLabelText('Weight (kg)')).toHaveValue(82)
    expect(screen.getByRole('checkbox', { name: 'Peanut allergy' })).toBeChecked()
    await user.click(screen.getByRole('button', { name: '2 · Craving' }))
    expect(cravingInput()).toHaveValue('High-protein burger')
    await user.click(screen.getByRole('button', { name: '3 · Your plan' }))
    expect(screen.getByText('Grilled Chicken Bowl')).toBeInTheDocument()
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    expect(axios.post.mock.calls[0][1]).toMatchObject({
      weight_kg: 82,
      health_conditions: ['peanut allergy'],
    })
  })

  // Old: "switches to the history tab". History is a small link now (§7).
  it('opens past plans from a link and comes back with everything kept', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<App />)
    await planFromStart(user)
    await screen.findByText('Grilled Chicken Bowl')

    await user.click(screen.getByRole('button', { name: 'Past plans' }))
    expect(screen.getByRole('heading', { name: 'History' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Meal History' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Saved Meals' })).toBeInTheDocument()
    // History looks up this visit's own user ID first.
    expect(screen.getByLabelText('User ID')).toHaveValue(axios.post.mock.calls[0][1].user_id)
    expect(screen.queryByText('Grilled Chicken Bowl')).not.toBeVisible()

    await user.click(screen.getByRole('button', { name: 'Back to your meal' }))
    expect(screen.getByText('Grilled Chicken Bowl')).toBeVisible()
    expect(screen.queryByRole('heading', { name: 'Meal History' })).not.toBeInTheDocument()
  })

  // Old: "switches to the calories tab". The separate estimate stays as a link.
  it('opens the calorie estimate from a link', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole('button', { name: 'Calorie estimate' }))
    expect(screen.getByRole('heading', { name: 'Calorie Expenditure' })).toBeInTheDocument()
    // Hidden, not unmounted: the flow keeps its state while the link is open.
    expect(
      screen.getByRole('heading', { name: 'Tell us about you', hidden: true }),
    ).not.toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Back to your meal' }))
    expect(screen.getByRole('heading', { name: 'Tell us about you' })).toBeVisible()
  })
})
