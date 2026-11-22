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

import { HOSTED_FEEDBACK_MESSAGE } from '../plan/feedback'
import { SAMPLE_PLAN } from '../plan/samplePlan'
import { STORED, TEST_USER_ID, renderApp } from '../../test/renderApp'

const STORED_PLAN = { ...SAMPLE_PLAN, request_id: 'req-00000001', saved_at: '2026-11-22T02:00:00Z' }
const SAVED = {
  request_id: 'req-00000001',
  meal_name: 'Chicken Fried Rice',
  saved: true,
  saved_at: '2026-11-22T03:00:00Z',
}

// GET /saved-meals and GET /meal-plans, answered by URL.
function serve({ saved = [], plans = [], fail = null } = {}) {
  axios.get.mockImplementation((url) => {
    if (fail) return Promise.reject(fail)
    if (url.includes('/saved-meals/')) return Promise.resolve({ data: { items: saved } })
    if (url.includes('/meal-plans/')) return Promise.resolve({ data: { items: plans } })
    return Promise.resolve({ data: {} })
  })
}

describe('My meals and past plans', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    axios.get.mockReset()
  })

  it("lists this device's saved meals and past plans on Home", async () => {
    serve({ saved: [SAVED, { ...SAVED, saved_at: '2026-11-22T01:00:00Z' }], plans: [STORED_PLAN] })
    renderApp({ stored: STORED })

    const meals = await screen.findByRole('region', { name: 'My meals' })
    // Saved twice, shown once, with its plan's numbers.
    expect(await within(meals).findAllByRole('link', { name: /Chicken Fried Rice/ })).toHaveLength(1)
    expect(within(meals).getByText('629 kcal')).toBeInTheDocument()
    expect(within(meals).getByText('Protein 27% · Carbs 46% · Fat 27%')).toBeInTheDocument()
    const past = screen.getByRole('region', { name: 'Past plans' })
    expect(within(past).getByText('For “chicken fried rice”')).toBeInTheDocument()
    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining(`/saved-meals/${TEST_USER_ID}`), {
      params: { limit: 50 },
    })
  })

  it('says what to do when there is nothing yet', async () => {
    serve()
    renderApp({ stored: STORED })
    expect(await screen.findByText('Meals you save from a plan show up here.')).toBeInTheDocument()
    expect(screen.getByText('Plans you make show up here.')).toBeInTheDocument()
  })

  it('opens a stored plan from My meals without planning again', async () => {
    serve({ saved: [SAVED], plans: [STORED_PLAN] })
    const user = userEvent.setup()
    renderApp({ stored: STORED, route: '/meals' })

    expect(screen.getByRole('heading', { level: 1, name: 'My meals' })).toBeInTheDocument()
    await user.click(await screen.findByRole('link', { name: /Chicken Fried Rice/ }))
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Chicken Fried Rice' }),
    ).toBeInTheDocument()
    expect(screen.getByText('For your craving “chicken fried rice”')).toBeInTheDocument()
    // Already saved on the server, so it can't be saved twice.
    expect(screen.getByRole('button', { name: 'Saved to My meals' })).toBeDisabled()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('lists past plans on their own page, leaving out infeasible ones', async () => {
    serve({
      plans: [
        STORED_PLAN,
        { request_id: 'req-00000002', plan_status: 'infeasible', meal_plan: null, saved_at: '1' },
      ],
    })
    renderApp({ stored: STORED, route: '/history' })
    expect(await screen.findAllByRole('link', { name: /Chicken Fried Rice/ })).toHaveLength(1)
    expect(screen.getByText(/lost when that server is replaced/)).toBeInTheDocument()
  })

  it('says when a plan is no longer in history', async () => {
    serve({ plans: [STORED_PLAN] })
    renderApp({ stored: STORED, route: '/plans/req-gone-0001' })
    expect(
      await screen.findByRole('heading', { name: 'This plan is no longer in your history' }),
    ).toBeInTheDocument()
  })

  it('explains a hosted server instead of failing', async () => {
    serve({ fail: { response: { status: 501, data: { detail: 'Not implemented' } } } })
    renderApp({ stored: STORED, route: '/meals' })
    expect(await screen.findByText(HOSTED_FEEDBACK_MESSAGE)).toBeInTheDocument()
  })

  it("shows its own sentence when the API can't be reached, or the backend's detail", async () => {
    serve({ fail: new Error('Network Error') })
    renderApp({ stored: STORED, route: '/history' })
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not load your meals. Check that the FastAPI backend is running on port 8000.',
    )
  })

  it("prefers the backend's detail when there is one", async () => {
    serve({ fail: { response: { status: 500, data: { detail: 'History store is locked' } } } })
    renderApp({ stored: STORED, route: '/history' })
    expect(await screen.findByRole('alert')).toHaveTextContent('History store is locked')
  })
})
