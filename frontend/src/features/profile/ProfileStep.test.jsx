import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'

import { STORAGE_KEY } from '../../app/storage'
import { backToPlan, goToProfile, planMeal as planCraving, renderApp } from '../../test/renderApp'

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

const planMeal = (user) => planCraving(user, 'fried rice')

// From the plan to the Profile page, to change a detail.
const toDetails = goToProfile

describe('Profile details', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends the profile with the meal request', async () => {
    const user = userEvent.setup()
    renderApp()

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
      user_id: expect.stringMatching(/^web-[0-9a-f-]{36}$/),
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

  it("sends today's workout only after the person says they worked out", async () => {
    const user = userEvent.setup()
    renderApp()

    expect(screen.queryByLabelText('Minutes')).not.toBeInTheDocument()
    await user.selectOptions(screen.getByLabelText("Today's workout"), 'trained')
    await user.clear(screen.getByLabelText('Minutes'))
    await user.type(screen.getByLabelText('Minutes'), '50')
    await user.type(screen.getByLabelText('Average heart rate (optional)'), '140')
    await planMeal(user)

    expect(axios.post.mock.calls[0][1]).toMatchObject({ duration_minutes: 50, heart_rate_bpm: 140 })
  })

  it('sends a rest day as 0 minutes', async () => {
    const user = userEvent.setup()
    renderApp()

    await user.selectOptions(screen.getByLabelText("Today's workout"), 'rest')
    await planMeal(user)

    expect(axios.post.mock.calls[0][1].duration_minutes).toBe(0)
  })

  it('shows a field message and sends nothing while a detail is out of range', async () => {
    const user = userEvent.setup()
    renderApp()

    await user.clear(screen.getByLabelText('Age'))
    await user.type(screen.getByLabelText('Age'), '130')

    const age = screen.getByLabelText('Age')
    expect(age).toHaveAttribute('aria-invalid', 'true')
    expect(age).toHaveAccessibleDescription('Age must be more than 0 and at most 120 years.')
    // The app can't be started, so no plan can be asked for, with an invalid detail.
    expect(screen.getByRole('button', { name: 'Save and start planning' })).toBeDisabled()
    expect(screen.getByText('Fix the highlighted details to continue.')).toBeInTheDocument()

    await user.type(age, '{Enter}')
    expect(screen.getByRole('heading', { name: 'Tell us about you' })).toBeInTheDocument()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('marks a plan stale when the profile changes, and re-plans with the new details', async () => {
    axios.post.mockResolvedValueOnce(PLAN).mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp()

    await planMeal(user)
    expect(await screen.findByText('Chicken Fried Rice')).toBeInTheDocument()
    expect(screen.queryByText(/Made for your previous details/)).not.toBeInTheDocument()

    await toDetails(user)
    await user.click(screen.getByRole('radio', { name: /Gain/ }))
    await backToPlan(user)
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
    renderApp()

    await planMeal(user)
    await screen.findByText('Chicken Fried Rice')
    await toDetails(user)
    await user.click(screen.getByRole('checkbox', { name: 'Gluten-free' }))
    await backToPlan(user)
    expect(screen.getByText(/Made for your previous details/)).toBeInTheDocument()
    await toDetails(user)
    await user.click(screen.getByRole('checkbox', { name: 'Gluten-free' }))
    await backToPlan(user)
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
    renderApp()

    await planMeal(user)
    expect(
      await screen.findByText(
        'The service could not use some of your details. Fix the highlighted fields.',
      ),
    ).toBeInTheDocument()
    await toDetails(user)
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
    renderApp()

    await planMeal(user)
    await screen.findByRole('alert')
    await toDetails(user)
    const weight = screen.getByLabelText('Weight (kg)')
    const height = screen.getByLabelText('Height (cm)')
    expect(screen.getByText('Input should be greater than 20')).toBeInTheDocument()

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

  it('says what a 422 naming no field on screen rejected', async () => {
    axios.post.mockRejectedValueOnce({
      response: {
        status: 422,
        data: { detail: [{ loc: ['body'], msg: 'Field required' }] },
      },
    })
    const user = userEvent.setup()
    renderApp()

    await planMeal(user)
    expect(
      await screen.findByText('The service rejected this request: body: Field required'),
    ).toBeInTheDocument()
  })

  // DEC-36 replaces "never in browser storage": the details are remembered on
  // this device under one key, only once the person starts, and never in a URL.
  it('remembers the profile only after starting, under one key, and never in the URL', async () => {
    axios.post.mockResolvedValueOnce(PLAN)
    const user = userEvent.setup()
    renderApp()
    const setItem = vi.spyOn(Storage.prototype, 'setItem')
    const pushState = vi.spyOn(window.history, 'pushState')
    const before = window.location.href

    await user.click(screen.getByRole('checkbox', { name: 'Kidney disease' }))
    expect(setItem).not.toHaveBeenCalled()
    await planMeal(user)
    await waitFor(() => expect(screen.getByText('Chicken Fried Rice')).toBeInTheDocument())

    expect(new Set(setItem.mock.calls.map(([key]) => key))).toEqual(new Set([STORAGE_KEY]))
    expect(pushState).not.toHaveBeenCalled()
    expect(window.location.href).toBe(before)
  })

  it('says where the details go and that it is not medical advice', () => {
    renderApp()
    expect(screen.getByRole('heading', { name: 'Tell us about you' })).toBeInTheDocument()
    expect(
      screen.getByText(/the server keeps a history of the plans it makes, including these details/),
    ).toBeInTheDocument()
    expect(screen.getByText('A planning aid, not medical advice.')).toBeInTheDocument()
  })

  it('reaches every profile control from the keyboard', async () => {
    const user = userEvent.setup()
    renderApp()

    // From the heading: one tab stop for the goal radio group, then the
    // fields, the chips, where you shop and the button to start.
    screen.getByRole('heading', { name: 'Tell us about you' }).focus()
    const expected = [
      screen.getByRole('radio', { name: /Maintain/ }),
      screen.getByLabelText('Age'),
      screen.getByLabelText('Sex'),
      screen.getByLabelText('Height (cm)'),
      screen.getByLabelText('Weight (kg)'),
      screen.getByLabelText('How active are you?'),
      screen.getByLabelText("Today's workout"),
      ...['Vegetarian', 'Vegan', 'Dairy-free', 'Gluten-free', 'Peanut allergy', 'Kidney disease'].map(
        (name) => screen.getByRole('checkbox', { name }),
      ),
      screen.getByLabelText(/Where you shop/),
      screen.getByRole('button', { name: 'Save and start planning' }),
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
