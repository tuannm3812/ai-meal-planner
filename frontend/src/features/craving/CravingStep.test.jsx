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

import { goToStep } from '../../test/flow'
import MealFlow from '../flow/MealFlow'

const plan = (name) => ({
  data: {
    plan_status: 'matched',
    meal_plan: { meal_definition: { structured_meal_name: name, ingredients: [] } },
    nutrition: {},
    shopping_list: {},
  },
})

const cravingInput = () => screen.getByLabelText(/Your craving/i)
const planButton = () => screen.getByRole('button', { name: 'Plan my meal' })

describe('Craving step', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fills the craving from a suggestion and sends it', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    const suggestions = screen.getByRole('list', { name: 'Or try one of these' })
    await user.click(within(suggestions).getByRole('button', { name: 'Salmon quinoa' }))
    expect(cravingInput()).toHaveValue('salmon quinoa')

    await user.click(planButton())
    expect(axios.post.mock.calls[0][1]).toMatchObject({ craving: 'salmon quinoa' })
  })

  it('picks a suggestion from the keyboard', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    screen.getByRole('button', { name: 'Chickpea curry' }).focus()
    await user.keyboard('{Enter}')
    expect(cravingInput()).toHaveValue('chickpea curry')
    // A suggestion is a button, not a submit: nothing is sent until asked.
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('says why a craving is refused and sends nothing', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'x')
    expect(cravingInput()).toHaveAttribute('aria-invalid', 'true')
    expect(cravingInput()).toHaveAccessibleDescription('Use at least 2 characters.')
    expect(planButton()).toBeDisabled()

    await user.clear(cravingInput())
    expect(cravingInput()).not.toHaveAttribute('aria-invalid')
    expect(planButton()).toBeDisabled()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('says when the location is emptied', async () => {
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'fried rice')
    await user.clear(screen.getByLabelText(/^Where you shop/))
    expect(screen.getByText('Enter a location.')).toBeInTheDocument()
    expect(planButton()).toBeDisabled()
  })

  it('maps a 422 on the craving back to its field until it is edited', async () => {
    axios.post.mockRejectedValueOnce({
      response: {
        status: 422,
        data: { detail: [{ loc: ['body', 'craving'], msg: 'Not a food we recognise' }] },
      },
    })
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'zzz')
    await user.click(planButton())
    expect(
      await screen.findByText(
        'The service could not use some of your details. Go back to the highlighted fields.',
      ),
    ).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Try another craving' }))
    expect(cravingInput()).toHaveAccessibleDescription('Not a food we recognise')

    // Editing the location leaves the craving's message; editing the craving clears it.
    await user.type(screen.getByLabelText(/^Where you shop/), ' West')
    expect(cravingInput()).toHaveAttribute('aria-invalid', 'true')
    await user.type(cravingInput(), 'z')
    expect(cravingInput()).not.toHaveAttribute('aria-invalid')
  })

  it('marks a plan stale when the craving or location changes, and re-plans', async () => {
    axios.post.mockResolvedValueOnce(plan('Chicken Fried Rice'))
    axios.post.mockResolvedValueOnce(plan('Salmon Quinoa Plate'))
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'fried rice')
    await user.click(planButton())
    await screen.findByText('Chicken Fried Rice')
    expect(screen.queryByRole('status')).not.toBeInTheDocument()

    await goToStep(user, '2 · Craving')
    await user.type(screen.getByLabelText(/^Where you shop/), ' West')
    await goToStep(user, '3 · Your plan')
    expect(screen.getByRole('status')).toHaveTextContent('Made for your previous details.')
    // The result still names the store area it was made for.
    expect(screen.getByText('For shopping near “Earlwood, NSW”')).toBeInTheDocument()
    expect(screen.queryByText(/Earlwood, NSW West/)).not.toBeInTheDocument()

    await goToStep(user, '2 · Craving')
    await user.clear(cravingInput())
    await user.type(cravingInput(), 'salmon')
    await goToStep(user, '3 · Your plan')
    await user.click(screen.getByRole('button', { name: 'Plan again with these details' }))
    expect(axios.post.mock.calls[1][1]).toMatchObject({
      craving: 'salmon',
      location: 'Earlwood, NSW West',
    })
    await screen.findByText('Salmon Quinoa Plate')
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    expect(screen.getByText(/For your craving .salmon./)).toBeInTheDocument()
  })

  function deferPost() {
    let resolve
    axios.post.mockImplementationOnce(
      () =>
        new Promise((done) => {
          resolve = done
        }),
    )
    return (value) => resolve(value)
  }

  it('drops a pending answer when the craving changes before it arrives', async () => {
    const answer = deferPost()
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'fried rice')
    await user.click(planButton())
    // Back to the craving while the plan is still being made.
    await goToStep(user, '2 · Craving')
    await user.clear(cravingInput())
    await user.type(cravingInput(), 'salmon')
    answer(plan('Chicken Fried Rice'))
    await goToStep(user, '3 · Your plan')

    expect(await screen.findByText(/Plan set aside/)).toBeInTheDocument()
    expect(screen.queryByText('Chicken Fried Rice')).not.toBeInTheDocument()

    axios.post.mockResolvedValueOnce(plan('Salmon Quinoa Plate'))
    await goToStep(user, '2 · Craving')
    expect(planButton()).toBeEnabled()
    await user.click(planButton())
    expect(axios.post.mock.calls[1][1]).toMatchObject({ craving: 'salmon' })
    await screen.findByText('Salmon Quinoa Plate')
    expect(screen.queryByText(/Plan set aside/)).not.toBeInTheDocument()
  })

  it('drops a pending answer when the profile changes before it arrives', async () => {
    const answer = deferPost()
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'fried rice')
    await user.click(planButton())
    await user.click(screen.getByRole('button', { name: 'Change your details' }))
    await user.click(screen.getByRole('checkbox', { name: 'Vegan' }))
    answer(plan('Chicken Fried Rice'))
    await goToStep(user, '3 · Your plan')

    expect(await screen.findByText(/Plan set aside/)).toBeInTheDocument()
    expect(screen.queryByText('Chicken Fried Rice')).not.toBeInTheDocument()
  })

  it('keeps a pending answer when an edit is undone before it arrives', async () => {
    const answer = deferPost()
    const user = userEvent.setup()
    render(<MealFlow initialStep="craving" />)

    await user.type(cravingInput(), 'fried rice')
    await user.click(planButton())
    // Whitespace the request trims away is not a change to what was asked.
    await goToStep(user, '2 · Craving')
    await user.type(cravingInput(), ' ')
    answer(plan('Chicken Fried Rice'))
    await goToStep(user, '3 · Your plan')

    expect(await screen.findByText('Chicken Fried Rice')).toBeInTheDocument()
    expect(screen.queryByText(/Plan set aside/)).not.toBeInTheDocument()
  })

  it('makes only promises that hold today', () => {
    render(<MealFlow initialStep="craving" />)
    expect(screen.getByText('Matched to a real menu')).toBeInTheDocument()
    expect(
      screen.getByText('No close match? You get a standard meal and a note saying so.'),
    ).toBeInTheDocument()
    expect(screen.getByText('Shopping list included')).toBeInTheDocument()
    // No claim that the standard meal is balanced or a good match.
    expect(screen.queryByText(/balanced/i)).not.toBeInTheDocument()
  })
})
