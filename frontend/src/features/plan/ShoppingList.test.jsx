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

import { STORED, backToPlan, goToProfile, planMeal, renderApp } from '../../test/renderApp'
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
    renderApp({ stored: STORED })
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

    // An unknown product is named after its ingredient, once, without "Generic".
    const rice = within(list).getByRole('checkbox', { name: /Cooked white rice/ })
    expect(rice.closest('label')).toHaveTextContent('Rough estimate')
    expect(rice.closest('label')).not.toHaveTextContent(/Generic|For cooked white rice/)

    expect(within(list).getByText('6 items')).toBeInTheDocument()
    expect(within(list).getByText('Estimated total').parentElement).toHaveTextContent('$24.50')
    // The banner carries the same total as a price tag.
    expect(screen.getByText('About $24.50 to shop')).toBeInTheDocument()
    expect(
      within(list).getByText('Prices are estimates from a local reference list, not live store prices.'),
    ).toBeInTheDocument()
    // The rough-estimate wording is explained once, under the list, not on every row.
    expect(within(list).getAllByText(/guessed from the item.s category/)).toHaveLength(1)
  })

  it('ticks items by mouse and keyboard, sending nothing', async () => {
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    const list = await planWith(user, SAMPLE_PLAN)
    expect(within(list).getByText('0 of 6 ticked')).toBeInTheDocument()
    const reads = axios.get.mock.calls.length

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
    expect(axios.get).toHaveBeenCalledTimes(reads)
  })

  it('starts a new plan with nothing ticked', async () => {
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    let list = await planWith(user, SAMPLE_PLAN)
    await user.click(within(list).getByRole('checkbox', { name: /Chicken Breast Fillets/ }))

    list = await planWith(user, { ...SAMPLE_PLAN, request_id: 'another-request' }, 'fried rice')
    expect(within(list).getByText('0 of 6 ticked')).toBeInTheDocument()
    expect(within(list).getByRole('checkbox', { name: /Chicken Breast Fillets/ })).not.toBeChecked()
  })

  it('keeps ticks while moving between pages on the same plan', async () => {
    const user = userEvent.setup()
    renderApp({ stored: STORED })
    await planWith(user, SAMPLE_PLAN)
    await user.click(screen.getByRole('checkbox', { name: /Chicken Breast Fillets/ }))

    await goToProfile(user)
    await backToPlan(user)
    expect(screen.getByRole('checkbox', { name: /Chicken Breast Fillets/ })).toBeChecked()
    expect(screen.getByText('1 of 6 ticked')).toBeInTheDocument()
    expect(axios.post).toHaveBeenCalledTimes(1)
  })

  it('says when the store is a guess for the area', async () => {
    const user = userEvent.setup()
    renderApp({ stored: STORED })
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
    renderApp({ stored: STORED })
    const list = await planWith(user, { ...SAMPLE_PLAN, shopping_list: shopping })

    expect(within(list).getByText('No shopping list came with this plan.')).toBeInTheDocument()
    expect(within(list).queryByRole('checkbox')).not.toBeInTheDocument()
    expect(within(list).queryByText('Estimated total')).not.toBeInTheDocument()
    expect(within(list).queryByText(/Prices are estimates/)).not.toBeInTheDocument()
    // The meal itself still shows.
    expect(screen.getByRole('region', { name: 'Chicken Fried Rice' })).toBeInTheDocument()
  })

  it('copies the list as text and prints only the list', async () => {
    const print = vi.spyOn(window, 'print').mockImplementation(() => {})
    // user-event puts its own clipboard on navigator; spy on it after setup.
    const user = userEvent.setup()
    const writeText = vi.spyOn(navigator.clipboard, 'writeText')
    renderApp({ stored: STORED })
    const list = await planWith(user, SAMPLE_PLAN)

    await user.click(within(list).getByRole('button', { name: 'Copy list' }))
    const text = writeText.mock.calls[0][0]
    expect(text).toContain('Shopping for Chicken Fried Rice')
    expect(text).toContain('Coles Supermarket, Earlwood, NSW 2206')
    expect(text).toMatch(/- Chicken Breast Fillets 500g: \$7\.80/)
    expect(text).toContain('Estimated total: $24.50')
    expect(within(list).getByRole('status')).toHaveTextContent('Copied to your clipboard.')

    await user.click(within(list).getByRole('button', { name: 'Print' }))
    expect(print).toHaveBeenCalledTimes(1)
    expect(list).toHaveAttribute('data-print', 'shopping')
    print.mockRestore()
  })
})
