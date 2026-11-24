import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'

import CaloriesTab from './CaloriesTab'

describe('CaloriesTab error text', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows its own fallback sentence when the backend is unreachable', async () => {
    // The only branch App.test.jsx does not cover: a rejection with no
    // `response` at all. Moving this tab onto useAsyncRequest risked replacing
    // this sentence with the hook's generic message, and the harness would not
    // have noticed - it only exercises the `detail` branch.
    axios.post.mockRejectedValueOnce(new Error('Network Error'))
    const user = userEvent.setup()
    render(<CaloriesTab />)

    await user.click(screen.getByRole('button', { name: 'Estimate my calories' }))

    expect(
      await screen.findByText(
        'Could not estimate your calories. Check your connection and try again.',
      ),
    ).toBeInTheDocument()
  })

  it("still prefers the backend's detail when there is one", async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Age out of range' } } })
    const user = userEvent.setup()
    render(<CaloriesTab />)

    await user.click(screen.getByRole('button', { name: 'Estimate my calories' }))

    expect(await screen.findByText('Age out of range')).toBeInTheDocument()
  })
})

describe('CaloriesTab request and result', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('sends no workout for "Not sure", as a plan does, so both give the same numbers', async () => {
    // It used to send a 30-minute workout every time, which replaces the
    // activity level's exercise (DEC-40): 2,267 kcal here, 2,895 on the plan.
    axios.post.mockResolvedValueOnce({
      data: {
        estimated_daily_expenditure_kcal: 2894.7,
        meal_calorie_budget_kcal: 2494.7,
        model_version: 'hist_gradient_boosting_deep_v0.1.0',
        confidence: 0.82,
        warnings: [],
        exercise: {
          duration_minutes: 30,
          heart_rate_bpm: 100,
          kcal: 116.4,
          defaulted: ['duration_minutes', 'heart_rate_bpm', 'body_temp_c'],
          replaces_activity_exercise: false,
        },
      },
    })
    const user = userEvent.setup()
    render(
      <CaloriesTab
        initial={{ age: '29', sex: 'male', heightCm: '178', weightKg: '82', activity: '1.55', goal: 'lose', workout: 'unsure' }}
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Estimate my calories' }))

    const body = axios.post.mock.calls[0][1]
    expect(body).toEqual({
      age: 29,
      sex: 'male',
      height_cm: 178,
      weight_kg: 82,
      activity_multiplier: 1.55,
      goal: 'weight_loss',
    })
    expect(await screen.findByText('2,895')).toBeInTheDocument()
    expect(screen.getByText('2,495')).toBeInTheDocument()
    // 28% of 2,495, as the plan page sizes one meal.
    expect(screen.getByText('699')).toBeInTheDocument()
    expect(screen.queryByText(/hist_gradient_boosting/)).not.toBeInTheDocument()
  })

  it('sends a rest day as zero minutes', async () => {
    const user = userEvent.setup()
    render(<CaloriesTab initial={{ workout: 'rest' }} />)

    await user.click(screen.getByRole('button', { name: 'Estimate my calories' }))

    expect(axios.post.mock.calls[0][1].duration_minutes).toBe(0)
  })
})
