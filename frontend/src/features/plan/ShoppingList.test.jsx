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

import { planMeal } from '../../test/flow'
import MealFlow from '../flow/MealFlow'
import { SAMPLE_PLAN } from './samplePlan'

async function planWith(user, data, craving = 'chicken fried rice') {
  axios.post.mockResolvedValueOnce({ data })
  await planMeal(user, craving)
  return screen.findByRole('region', { name: 'Shopping list' })
}

describe('Shopping list', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('lists items by aisle with prices, the total and the estimate note', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)
    const list = await planWith(user, SAMPLE_PLAN)

    expect(within(list).getByText('For shopping near “Earlwood, NSW”')).toBeInTheDocument()
    expect(within(list).getByText('Coles Supermarket · Earlwood, NSW 2206')).toBeInTheDocument()
    expect(within(list).queryByText(/likely store/)).not.toBeInTheDocument()

    const grocery = within(list).getByRole('group', { name: 'Grocery' })
    expect(within(grocery).getAllByRole('checkbox')).toHaveLength(3)
    const meat = within(list).getByRole('group', { name: 'Meat & Poultry' })
    expect(within(meat).getByText('Chicken Breast Fillets 500g')).toBeInTheDocument()
    expect(within(meat).getByText('$7.80')).toBeInTheDocument()
    expect(within(meat).queryByText(/guessed/)).not.toBeInTheDocument()

    const rice = within(list).getByRole('checkbox', { name: /Generic cooked white rice/ })
    expect(rice.closest('label')).toHaveTextContent(
      'For cooked white rice · Product and price guessed from its category',
    )

    expect(within(list).getByText('Estimated total').parentElement).toHaveTextContent('$24.50')
    expect(
      within(list).getByText('Prices are estimates from a local reference list, not live store prices.'),
    ).toBeInTheDocument()
  })

  it('ticks items by mouse and keyboard, sending nothing', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)
    const list = await planWith(user, SAMPLE_PLAN)
    expect(within(list).getByText('0 of 6 ticked')).toBeInTheDocument()

    await user.click(within(list).getByRole('checkbox', { name: /Chicken Breast Fillets/ }))
    const soy = within(list).getByRole('checkbox', { name: /Soy Sauce 250ml/ })
    soy.focus()
    await user.keyboard(' ')
    expect(soy).toBeChecked()
    expect(within(list).getByText('2 of 6 ticked')).toBeInTheDocument()

    await user.keyboard(' ')
    expect(soy).not.toBeChecked()
    expect(within(list).getByText('1 of 6 ticked')).toBeInTheDocument()
    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(axios.get).not.toHaveBeenCalled()
  })

  it('starts a new plan with nothing ticked', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)
    let list = await planWith(user, SAMPLE_PLAN)
    await user.click(within(list).getByRole('checkbox', { name: /Chicken Breast Fillets/ }))

    list = await planWith(user, { ...SAMPLE_PLAN, request_id: 'another-request' }, 'fried rice')
    expect(within(list).getByText('0 of 6 ticked')).toBeInTheDocument()
    expect(within(list).getByRole('checkbox', { name: /Chicken Breast Fillets/ })).not.toBeChecked()
  })

  it('says when the store is a guess for the area', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)
    const list = await planWith(user, {
      ...SAMPLE_PLAN,
      shopping_list: {
        ...SAMPLE_PLAN.shopping_list,
        store_details: {
          store_name: 'Local Supermarket',
          address: 'Near Perth',
          location_source: 'generic_estimate',
        },
      },
    })
    expect(within(list).getByText(/A likely store for your area/)).toBeInTheDocument()
  })

  it.each([
    ['an empty list', { ...SAMPLE_PLAN.shopping_list, shopping_list: [] }],
    ['no list at all', null],
  ])('shows its empty state for %s, with no total or note', async (_case, shopping) => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)
    const list = await planWith(user, { ...SAMPLE_PLAN, shopping_list: shopping })

    expect(within(list).getByText('No shopping list came with this plan.')).toBeInTheDocument()
    expect(within(list).queryByRole('checkbox')).not.toBeInTheDocument()
    expect(within(list).queryByText('Estimated total')).not.toBeInTheDocument()
    expect(within(list).queryByText(/Prices are estimates/)).not.toBeInTheDocument()
    // The meal itself still shows.
    expect(screen.getByRole('region', { name: 'Chicken Fried Rice' })).toBeInTheDocument()
  })
})
