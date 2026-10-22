import { render, screen, waitFor } from '@testing-library/react'
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

const PLAN = {
  data: {
    plan_status: 'matched',
    meal_plan: {
      meal_definition: { structured_meal_name: 'Chicken Fried Rice', ingredients: [] },
    },
    nutrition: {},
    shopping_list: {},
  },
}

async function planMeal(user) {
  await user.type(screen.getByLabelText(/Craving Input/i), 'fried rice')
  await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))
}

describe('Profile step', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends the profile with the meal request', async () => {
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.click(screen.getByRole('radio', { name: /Lose weight/ }))
    await user.clear(screen.getByLabelText('Age'))
    await user.type(screen.getByLabelText('Age'), '41')
    await user.selectOptions(screen.getByLabelText('Sex'), 'male')
    await user.clear(screen.getByLabelText('Height (cm)'))
    await user.type(screen.getByLabelText('Height (cm)'), '181')
    await user.clear(screen.getByLabelText('Weight (kg)'))
    await user.type(screen.getByLabelText('Weight (kg)'), '82.5')
    await user.selectOptions(screen.getByLabelText('How active are you?'), '1.725')
    await user.click(screen.getByRole('checkbox', { name: 'Vegan' }))
    await user.click(screen.getByRole('checkbox', { name: 'Peanut allergy' }))
    await planMeal(user)

    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(axios.post.mock.calls[0][1]).toEqual({
      user_id: 'user_123',
      craving: 'fried rice',
      location: 'Earlwood, NSW',
      goal: 'lose',
      age: 41,
      sex: 'male',
      height_cm: 181,
      weight_kg: 82.5,
      activity_multiplier: 1.725,
      dietary_preferences: ['vegan'],
      health_conditions: ['peanut allergy'],
    })
  })

  it('shows a field message and sends nothing while a detail is out of range', async () => {
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.clear(screen.getByLabelText('Age'))
    await user.type(screen.getByLabelText('Age'), '130')
    await user.type(screen.getByLabelText(/Craving Input/i), 'fried rice')

    const age = screen.getByLabelText('Age')
    expect(age).toHaveAttribute('aria-invalid', 'true')
    expect(age).toHaveAccessibleDescription('Age must be more than 0 and at most 120 years.')
    expect(screen.getByRole('button', { name: 'Generate Meal Plan' })).toBeDisabled()
    expect(screen.getByText('Fix your details above to plan a meal.')).toBeInTheDocument()

    await user.type(screen.getByLabelText(/Craving Input/i), '{Enter}')
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('marks a plan stale when the profile changes, and re-plans with the new details', async () => {
    axios.post.mockResolvedValueOnce(PLAN).mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await planMeal(user)
    expect(await screen.findByText('Chicken Fried Rice')).toBeInTheDocument()
    expect(screen.queryByText(/Made for your previous details/)).not.toBeInTheDocument()

    await user.click(screen.getByRole('radio', { name: /Gain/ }))
    expect(screen.getByRole('status')).toHaveTextContent('Made for your previous details.')
    // The plan stays visible, labelled as made for the old details.
    expect(screen.getByText('Chicken Fried Rice')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Plan again with these details' }))
    expect(axios.post).toHaveBeenCalledTimes(2)
    expect(axios.post.mock.calls[1][1]).toMatchObject({ goal: 'gain', craving: 'fried rice' })
    await screen.findByText('Chicken Fried Rice')
    expect(screen.queryByText(/Made for your previous details/)).not.toBeInTheDocument()
  })

  it('drops the stale mark when an edit is undone', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await planMeal(user)
    await screen.findByText('Chicken Fried Rice')
    const chip = screen.getByRole('checkbox', { name: 'Gluten-free' })
    await user.click(chip)
    expect(screen.getByText(/Made for your previous details/)).toBeInTheDocument()
    await user.click(chip)
    expect(screen.queryByText(/Made for your previous details/)).not.toBeInTheDocument()
  })

  it('maps a 422 back to the field it names until that detail is edited', async () => {
    axios.post.mockRejectedValueOnce({
      response: {
        status: 422,
        data: { detail: [{ loc: ['body', 'weight_kg'], msg: 'Input should be greater than 20' }] },
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await planMeal(user)
    expect(
      await screen.findByText(
        'The service could not use some of your details. Check the highlighted fields.',
      ),
    ).toBeInTheDocument()
    const weight = screen.getByLabelText('Weight (kg)')
    expect(weight).toHaveAttribute('aria-invalid', 'true')
    expect(weight).toHaveAccessibleDescription('Input should be greater than 20')

    await user.clear(weight)
    await user.type(weight, '65')
    expect(weight).not.toHaveAttribute('aria-invalid')
    expect(weight).not.toHaveAccessibleDescription()
  })

  it('clears a server error only for the field that was edited', async () => {
    axios.post.mockRejectedValueOnce({
      response: {
        status: 422,
        data: {
          detail: [
            { loc: ['body', 'weight_kg'], msg: 'Input should be greater than 20' },
            { loc: ['body', 'height_cm'], msg: 'Input should be greater than 80' },
          ],
        },
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await planMeal(user)
    const weight = screen.getByLabelText('Weight (kg)')
    const height = screen.getByLabelText('Height (cm)')
    await screen.findByText('Input should be greater than 20')

    // An unrelated edit leaves both messages in place.
    await user.click(screen.getByRole('radio', { name: /Gain/ }))
    expect(weight).toHaveAccessibleDescription('Input should be greater than 20')
    expect(height).toHaveAccessibleDescription('Input should be greater than 80')

    // Editing the weight clears its message only.
    await user.clear(weight)
    await user.type(weight, '65')
    expect(weight).not.toHaveAttribute('aria-invalid')
    expect(height).toHaveAttribute('aria-invalid', 'true')
    expect(height).toHaveAccessibleDescription('Input should be greater than 80')
  })

  it('says what a 422 on a non-profile field rejected', async () => {
    axios.post.mockRejectedValueOnce({
      response: {
        status: 422,
        data: { detail: [{ loc: ['body', 'craving'], msg: 'String should have at most 180 characters' }] },
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await planMeal(user)
    expect(
      await screen.findByText(
        'The service rejected this request: craving: String should have at most 180 characters',
      ),
    ).toBeInTheDocument()
  })

  it('keeps the profile out of the URL and browser storage', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const setItem = vi.spyOn(Storage.prototype, 'setItem')
    const pushState = vi.spyOn(window.history, 'pushState')
    const replaceState = vi.spyOn(window.history, 'replaceState')
    const before = window.location.href
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.click(screen.getByRole('checkbox', { name: 'Kidney disease' }))
    await planMeal(user)
    await waitFor(() => expect(screen.getByText('Chicken Fried Rice')).toBeInTheDocument())

    expect(setItem).not.toHaveBeenCalled()
    expect(pushState).not.toHaveBeenCalled()
    expect(replaceState).not.toHaveBeenCalled()
    expect(window.location.href).toBe(before)
  })

  it('says where the details go and that it is not medical advice', () => {
    render(<MealPlanTab />)
    expect(screen.getByRole('heading', { name: 'Tell us about you' })).toBeInTheDocument()
    expect(
      screen.getByText(/the server keeps a history of the plans it makes, including these details/),
    ).toBeInTheDocument()
    expect(screen.getByText('A planning aid, not medical advice.')).toBeInTheDocument()
  })

  it('reaches every profile control from the keyboard', async () => {
    const user = userEvent.setup()
    render(<MealPlanTab />)

    // One tab stop for the goal radio group, then the fields and the chips.
    const expected = [
      screen.getByRole('radio', { name: /Maintain/ }),
      screen.getByLabelText('Age'),
      screen.getByLabelText('Sex'),
      screen.getByLabelText('Height (cm)'),
      screen.getByLabelText('Weight (kg)'),
      screen.getByLabelText('How active are you?'),
      ...['Vegetarian', 'Vegan', 'Dairy-free', 'Gluten-free', 'Peanut allergy', 'Kidney disease'].map(
        (name) => screen.getByRole('checkbox', { name }),
      ),
    ]
    for (const control of expected) {
      await user.tab()
      expect(control).toHaveFocus()
    }

    // Arrow keys move the goal choice, as in any radio group.
    screen.getByRole('radio', { name: /Maintain/ }).focus()
    await user.keyboard('{ArrowRight}')
    expect(screen.getByRole('radio', { name: /Gain/ })).toBeChecked()
  })
})
