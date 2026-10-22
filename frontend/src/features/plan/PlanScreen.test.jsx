import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'

import MealPlanTab from '../mealPlan/MealPlanTab'
import { DEFAULT_RETRY_SECONDS } from './failures'
import { SAMPLE_PLAN } from './samplePlan'

const planButton = () => screen.getByRole('button', { name: 'Generate Meal Plan' })

async function plan(user, craving = 'chicken fried rice') {
  await user.type(screen.getByLabelText(/Craving Input/i), craving)
  await user.click(planButton())
}

const reject = (status, data = {}, headers = {}) =>
  axios.post.mockRejectedValueOnce({ response: { status, data, headers } })

describe('Plan screen', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows the header, badges and estimated-nutrition notice for a real response', async () => {
    axios.post.mockResolvedValueOnce({ data: SAMPLE_PLAN })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const header = await screen.findByRole('region', { name: 'Chicken Fried Rice' })
    expect(within(header).getByText('For your craving “chicken fried rice”')).toBeInTheDocument()
    expect(within(header).getByText('Close menu match')).toBeInTheDocument()
    expect(within(header).getByText('Portions rebalanced')).toBeInTheDocument()
    expect(within(header).getByText('Some nutrition estimated')).toBeInTheDocument()
    expect(
      within(header).getByText(
        /3 of 6 ingredients use estimated nutrition from local tables, so these numbers are approximate\. “On target” is measured against those same tables/,
      ),
    ).toBeInTheDocument()
  })

  it('shows calories against the target, grams, and the served split in its bands', async () => {
    axios.post.mockResolvedValueOnce({ data: SAMPLE_PLAN })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const energy = await screen.findByRole('region', { name: 'Calories' })
    expect(within(energy).getByText('629 kcal')).toBeInTheDocument()
    expect(within(energy).getByText('Meal target: 625 kcal')).toBeInTheDocument()
    expect(within(energy).getByText('42 g')).toBeInTheDocument()
    expect(within(energy).getByText('71 g')).toBeInTheDocument()
    expect(within(energy).getByText('18 g')).toBeInTheDocument()

    const balance = screen.getByRole('region', { name: 'Balance' })
    expect(within(balance).getAllByText('27%')).toHaveLength(2)
    expect(within(balance).getByText('46%')).toBeInTheDocument()
    expect(within(balance).getByText(/range 45–65%/)).toBeInTheDocument()
    expect(within(balance).queryByText('(outside)')).not.toBeInTheDocument()
    expect(screen.getByTestId('band-carbs')).toHaveStyle({ left: '45%', width: '20%' })
  })

  it('tags each served ingredient and keeps the notes collapsed', async () => {
    axios.post.mockResolvedValueOnce({ data: SAMPLE_PLAN })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const list = await screen.findByRole('region', { name: 'Ingredients' })
    const rice = within(list).getByText('cooked white rice').closest('li')
    expect(within(rice).getByText('Estimated')).toBeInTheDocument()
    expect(within(rice).getByText('200 g')).toBeInTheDocument()
    const egg = within(list).getByText('whole egg').closest('li')
    expect(within(egg).getByText('Reference')).toBeInTheDocument()

    const details = screen.getByText('How this plan was made').closest('details')
    expect(details).not.toHaveAttribute('open')
    await user.click(screen.getByText('How this plan was made'))
    expect(details).toHaveAttribute('open')
    expect(within(details).getByText(/default 30-minute workout/)).toBeVisible()
  })

  it('marks a macro outside its range and keeps the service verdict', async () => {
    axios.post.mockResolvedValueOnce({
      data: {
        ...SAMPLE_PLAN,
        nutrition: { ...SAMPLE_PLAN.nutrition, total_protein: 10, total_carbs: 90, total_fat: 10 },
        macro_balance: { ...SAMPLE_PLAN.macro_balance, outcome: 'no_feasible_balance' },
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const header = await screen.findByRole('region', { name: 'Chicken Fried Rice' })
    expect(within(header).getByText('Outside the ranges')).toBeInTheDocument()
    const balance = screen.getByRole('region', { name: 'Balance' })
    // 490 kcal: protein 8% (below 10), carbs 73% (above 65), fat 18% (below 20).
    expect(within(balance).getAllByText('(outside)')).toHaveLength(3)
    expect(within(balance).getByText('73%')).toBeInTheDocument()
  })

  it('renders an older response without balance metadata, inventing nothing', async () => {
    const older = { ...SAMPLE_PLAN, calorie_budget: undefined }
    delete older.macro_balance
    axios.post.mockResolvedValueOnce({ data: older })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const header = await screen.findByRole('region', { name: 'Chicken Fried Rice' })
    expect(within(header).queryByText(/On target|rebalanced|Outside/)).not.toBeInTheDocument()
    expect(within(header).queryByText(/measured against those same tables/)).not.toBeInTheDocument()
    // The bars still come from the served nutrition; the target from reconciliation.
    expect(screen.getByRole('region', { name: 'Balance' })).toBeInTheDocument()
    expect(screen.getByText('Meal target: 625 kcal')).toBeInTheDocument()
    expect(screen.queryByText(/estimated daily energy/)).not.toBeInTheDocument()
  })

  it('offers a way back from an infeasible plan without losing anything', async () => {
    axios.post.mockResolvedValueOnce({
      data: {
        plan_status: 'infeasible',
        infeasible_reason: 'No meal satisfies these dietary and health constraints.',
        meal_plan: null,
        nutrition: null,
        shopping_list: null,
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user, 'peanut noodles')

    expect(await screen.findByText('No meal fits these constraints')).toBeInTheDocument()
    expect(screen.getByText('No meal satisfies these dietary and health constraints.')).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Calories' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Try another craving' }))
    expect(screen.getByLabelText(/Craving Input/i)).toHaveFocus()
    expect(screen.getByLabelText(/Craving Input/i)).toHaveValue('peanut noodles')
    await user.click(screen.getByRole('button', { name: 'Change your details' }))
    expect(screen.getByRole('heading', { name: 'Tell us about you' })).toHaveFocus()
  })

  it('shows an indeterminate loading state with no invented stages', async () => {
    axios.post.mockImplementationOnce(() => new Promise(() => {}))
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    expect(screen.getByText('Planning your meal…', { selector: 'h2' })).toBeInTheDocument()
    expect(screen.queryByText(/agents/i)).not.toBeInTheDocument()
  })
})

describe('Plan screen failures', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it.each([
    [401, 'missing_or_invalid_api_key', /this app does not send one/],
    [403, 'insufficient_scope', /not allowed to plan meals/],
  ])('says a %i server needs an API key and offers no retry', async (status, code, body) => {
    reject(status, { code, detail: 'from the server' })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('This server needs an API key')
    expect(alert).toHaveTextContent(body)
    expect(within(alert).queryByRole('button', { name: 'Try again' })).not.toBeInTheDocument()
  })

  it('waits out the Retry-After pause after a 429, then retries', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    reject(429, { code: 'rate_limited' }, { 'retry-after': '3' })
    axios.post.mockResolvedValueOnce({ data: SAMPLE_PLAN })
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<MealPlanTab />)
    await plan(user)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Too many requests, try again shortly')
    expect(alert).toHaveTextContent('You can try again in about 3 seconds.')
    const retry = within(alert).getByRole('button', { name: 'Try again' })
    expect(retry).toBeDisabled()

    await act(async () => {
      vi.advanceTimersByTime(3000)
    })
    expect(retry).toBeEnabled()
    await user.click(retry)
    expect(axios.post).toHaveBeenCalledTimes(2)
    expect(await screen.findByRole('region', { name: 'Chicken Fried Rice' })).toBeInTheDocument()
  })

  it.each([
    ['clicking the plan button', async (user) => user.click(planButton())],
    ['pressing Enter in the craving', async (user) => user.type(screen.getByLabelText(/Craving Input/i), '{Enter}')],
  ])('sends nothing during the pause by %s', async (_route, send) => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    reject(429, { code: 'rate_limited' }, { 'retry-after': '60' })
    axios.post.mockResolvedValueOnce({ data: SAMPLE_PLAN })
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<MealPlanTab />)
    await plan(user)
    await screen.findByRole('alert')

    expect(planButton()).toBeDisabled()
    await send(user)
    expect(axios.post).toHaveBeenCalledTimes(1)

    await act(async () => {
      vi.advanceTimersByTime(60_000)
    })
    expect(planButton()).toBeEnabled()
    await send(user)
    expect(axios.post).toHaveBeenCalledTimes(2)
    expect(await screen.findByRole('region', { name: 'Chicken Fried Rice' })).toBeInTheDocument()
  })

  it('holds the default pause for every route when Retry-After cannot be read', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    reject(429, { code: 'rate_limited' })
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<MealPlanTab />)
    await plan(user)
    await screen.findByRole('alert')

    await user.type(screen.getByLabelText(/Craving Input/i), '{Enter}')
    expect(axios.post).toHaveBeenCalledTimes(1)
    await act(async () => {
      vi.advanceTimersByTime((DEFAULT_RETRY_SECONDS - 1) * 1000)
    })
    expect(planButton()).toBeDisabled()
    await act(async () => {
      vi.advanceTimersByTime(1000)
    })
    expect(planButton()).toBeEnabled()
  })

  it('uses its default pause when Retry-After cannot be read', async () => {
    reject(429, { code: 'rate_limited' })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      `You can try again in about ${DEFAULT_RETRY_SECONDS} seconds.`,
    )
  })

  it("shows the service's message when nutrition could not be verified", async () => {
    reject(502, {
      code: 'unverified_required',
      detail: 'Nutrition verification is temporarily unavailable.',
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Nutrition could not be verified')
    expect(alert).toHaveTextContent('Nutrition verification is temporarily unavailable.')
    expect(within(alert).queryByRole('button')).not.toBeInTheDocument()
  })

  it('says planning is unavailable on a 503 and retries straight away', async () => {
    reject(503, { detail: 'Meal retrieval is temporarily unavailable. Please try again shortly.' })
    axios.post.mockResolvedValueOnce({ data: SAMPLE_PLAN })
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Planning is unavailable right now')
    expect(alert).toHaveTextContent('Meal retrieval is temporarily unavailable.')
    await user.click(within(alert).getByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('region', { name: 'Chicken Fried Rice' })).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('keeps the unreachable copy, with a retry', async () => {
    axios.post.mockRejectedValueOnce(new Error('Network Error'))
    const user = userEvent.setup()
    render(<MealPlanTab />)
    await plan(user)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Could not reach the meal planner')
    expect(within(alert).getByRole('button', { name: 'Try again' })).toBeEnabled()
  })
})
