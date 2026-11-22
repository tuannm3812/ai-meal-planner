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

import { STORED, TEST_USER_ID, planMeal, renderApp } from '../../test/renderApp'
import { HOSTED_FEEDBACK_MESSAGE } from './feedback'
import { SAMPLE_PLAN } from './samplePlan'

const PLAN = { ...SAMPLE_PLAN, request_id: 'req-00000001' }

async function openPlan(user) {
  axios.post.mockResolvedValueOnce({ data: PLAN })
  renderApp({ stored: STORED })
  await planMeal(user)
  await screen.findByRole('heading', { level: 1, name: 'Chicken Fried Rice' })
}

const feedbackCalls = () => axios.post.mock.calls.filter(([url]) => url.endsWith('/meal-feedback'))

describe('Plan actions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('saves the meal once, with the plan it came from', async () => {
    const user = userEvent.setup()
    await openPlan(user)

    await user.click(screen.getByRole('button', { name: 'Save meal' }))
    expect(feedbackCalls()).toHaveLength(1)
    expect(feedbackCalls()[0][1]).toEqual({
      user_id: TEST_USER_ID,
      request_id: 'req-00000001',
      meal_id: 'chicken_fried_rice',
      meal_name: 'Chicken Fried Rice',
      saved: true,
    })
    expect(await screen.findByRole('button', { name: 'Saved to My meals' })).toBeDisabled()
  })

  it('sends a star rating with an optional note, by keyboard', async () => {
    const user = userEvent.setup()
    await openPlan(user)

    const card = screen.getByRole('region', { name: 'How was it?' })
    expect(within(card).getByRole('button', { name: 'Save rating' })).toBeDisabled()
    within(card).getByRole('radio', { name: '1 star' }).focus()
    await user.keyboard('{ArrowRight}{ArrowRight}{ArrowRight}')
    expect(within(card).getByRole('radio', { name: '4 stars' })).toBeChecked()
    await user.type(within(card).getByLabelText('A note (optional)'), '  Would make again  ')
    await user.click(within(card).getByRole('button', { name: 'Save rating' }))

    expect(feedbackCalls()[0][1]).toMatchObject({
      request_id: 'req-00000001',
      rating: 4,
      notes: 'Would make again',
    })
    expect(await within(card).findByRole('status')).toHaveTextContent('You rated it 4 out of 5.')
    expect(within(card).queryByRole('button', { name: 'Save rating' })).not.toBeInTheDocument()
  })

  it('hides saving and rating once the server says it is hosted', async () => {
    axios.post.mockResolvedValueOnce({ data: PLAN })
    axios.post.mockRejectedValueOnce({ response: { status: 501, data: {} } })
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await planMeal(user)
    await user.click(await screen.findByRole('button', { name: 'Save meal' }))

    expect(await screen.findByText(HOSTED_FEEDBACK_MESSAGE)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Save meal/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'How was it?' })).not.toBeInTheDocument()
    // Planning still works.
    expect(screen.getByRole('region', { name: 'Shopping list' })).toBeInTheDocument()
  })

  it("says why a save failed and keeps the button", async () => {
    axios.post.mockResolvedValueOnce({ data: PLAN })
    axios.post.mockRejectedValueOnce({ response: { status: 500, data: { detail: 'Disk full' } } })
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await planMeal(user)
    await user.click(await screen.findByRole('button', { name: 'Save meal' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Disk full')
    expect(screen.getByRole('button', { name: 'Save meal' })).toBeEnabled()
  })

  it('plans a runner-up with the same details and its name as the craving', async () => {
    const user = userEvent.setup()
    await openPlan(user)

    const also = screen.getByRole('region', { name: 'Also close to your craving' })
    const options = within(also).getAllByRole('button')
    expect(options.map((button) => button.textContent)).not.toContain('Chicken Fried Rice')

    axios.post.mockResolvedValueOnce({
      data: {
        ...PLAN,
        request_id: 'req-00000002',
        meal_plan: {
          ...PLAN.meal_plan,
          meal_definition: { ...PLAN.meal_plan.meal_definition, structured_meal_name: 'Tofu Fried Rice' },
        },
      },
    })
    await user.click(within(also).getByRole('button', { name: 'Tofu Fried Rice' }))
    const [, payload] = axios.post.mock.calls[1]
    expect(payload).toMatchObject({ craving: 'Tofu Fried Rice', age: 34, location: 'Earlwood, NSW' })
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Tofu Fried Rice' }),
    ).toBeInTheDocument()
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
})
