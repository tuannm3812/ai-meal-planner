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

import MealPlanTab from './MealPlanTab'

describe('MealPlanTab error text', () => {
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
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'High-protein burger')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(
      await screen.findByText(
        'Could not generate a meal plan. Check that the FastAPI backend is running on port 8000.',
      ),
    ).toBeInTheDocument()
  })

  it("still prefers the backend's detail when there is one", async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Craving too short' } } })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'x')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('Craving too short')).toBeInTheDocument()
  })

  it('clears the previously rendered plan when a retry fails', async () => {
    // Pins the reset()-before-run() contract: useAsyncRequest's `run` never
    // clears `data` on its own, so MealPlanTab must call `clearMealPlan()`
    // before firing a second request. Without that call, a failed retry
    // would leave the first plan rendered next to the new error.
    axios.post.mockResolvedValueOnce({
      data: {
        meal_plan: {
          meal_definition: { structured_meal_name: 'Grilled Chicken Bowl', ingredients: [] },
        },
        nutrition: {},
        shopping_list: {},
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'High-protein burger')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))
    expect(await screen.findByText('Grilled Chicken Bowl')).toBeInTheDocument()

    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Backend exploded again' } } })
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('Backend exploded again')).toBeInTheDocument()
    expect(screen.queryByText('Grilled Chicken Bowl')).not.toBeInTheDocument()
  })

  it('shows the reason instead of an empty plan when no meal is feasible', async () => {
    // G3: an infeasible request is a 200 with plan_status "infeasible" and
    // null meal sections. Rendering MealPlanResult for it would show a
    // hollow "plan" with zeroed macros and no ingredients.
    axios.post.mockResolvedValueOnce({
      data: {
        status: 'success',
        plan_status: 'infeasible',
        infeasible_reason: 'No meal satisfies these dietary and health constraints.',
        meal_plan: null,
        nutrition: null,
        shopping_list: null,
        reconciliation: null,
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'tofu')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('No meal fits these constraints')).toBeInTheDocument()
    expect(
      screen.getByText('No meal satisfies these dietary and health constraints.'),
    ).toBeInTheDocument()
    // MealPlanResult's own section titles must be absent.
    expect(screen.queryByText('Meal Overview')).not.toBeInTheDocument()
    expect(screen.queryByText('Supermarket')).not.toBeInTheDocument()
  })

  it('shows the macro split and the target result the service reports', async () => {
    axios.post.mockResolvedValueOnce({
      data: {
        plan_status: 'matched',
        meal_plan: {
          meal_definition: { structured_meal_name: 'Chicken Fried Rice', ingredients: [] },
          metadata: {
            warnings: ['Rebalanced ingredient portions toward the recommended split.'],
          },
        },
        nutrition: {},
        shopping_list: {},
        macro_balance: {
          outcome: 'rebalanced',
          target_meal_calories: 700,
          macro_percent_before: { protein: 41.2, carbs: 42.6, fat: 16.2 },
          macro_percent_after: { protein: 29.6, carbs: 47.4, fat: 23.0 },
        },
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'chicken fried rice')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('Portions rebalanced')).toBeInTheDocument()
    // The split after rebalancing is the one that ships, not the one before.
    expect(screen.getByText('30%')).toBeInTheDocument()
    expect(screen.getByText('47%')).toBeInTheDocument()
    expect(screen.getByText('23%')).toBeInTheDocument()
    expect(screen.queryByText('41%')).not.toBeInTheDocument()
    expect(screen.getByText('Meal target: 700 kcal')).toBeInTheDocument()
    expect(
      screen.getByText('Rebalanced ingredient portions toward the recommended split.'),
    ).toBeInTheDocument()
    expect(screen.queryByText(/Nothing on the menu/)).not.toBeInTheDocument()
  })

  it('says when an off-menu craving got a standard meal instead', async () => {
    axios.post.mockResolvedValueOnce({
      data: {
        plan_status: 'fallback',
        meal_plan: {
          meal_definition: {
            structured_meal_name: 'High-Protein Turkey Burger Bowl',
            ingredients: [],
          },
          metadata: { warnings: [] },
        },
        nutrition: {},
        shopping_list: {},
        macro_balance: {
          outcome: 'in_range',
          target_meal_calories: 650,
          macro_percent_before: { protein: 31, carbs: 46, fat: 23 },
        },
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'pizza')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(
      await screen.findByText(/Nothing on the menu is a close match for/),
    ).toBeInTheDocument()
    expect(screen.getByText('On target')).toBeInTheDocument()
  })

  it('shows no quality section for a response without one', async () => {
    // An older API, or the existing tests' minimal responses, carry no
    // macro_balance, plan_status or warnings.
    axios.post.mockResolvedValueOnce({
      data: {
        meal_plan: {
          meal_definition: { structured_meal_name: 'Grilled Chicken Bowl', ingredients: [] },
        },
        nutrition: {},
        shopping_list: {},
      },
    })
    const user = userEvent.setup()
    render(<MealPlanTab />)

    await user.type(screen.getByLabelText(/Craving Input/i), 'chicken')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('Grilled Chicken Bowl')).toBeInTheDocument()
    expect(screen.queryByText('Meal Quality')).not.toBeInTheDocument()
  })
})
