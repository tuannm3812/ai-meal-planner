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
import App from './App'

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing and shows the tab bar', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1, name: /meal planning dashboard/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Meal Plan' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Calories' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'History' })).toBeInTheDocument()
  })

  it('shows the meal plan tab content by default', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Plan Request' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Calorie Expenditure' })).not.toBeInTheDocument()
  })

  it('switches to the calories tab', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: 'Calories' }))
    expect(screen.getByRole('heading', { name: 'Calorie Expenditure' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Plan Request' })).not.toBeInTheDocument()
  })

  it('switches to the history tab', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: 'History' }))
    // Exact match: the aside heading is literally "History", distinct from the
    // "Meal History" / "Saved Meals" section headings that also render on this tab.
    expect(screen.getByRole('heading', { name: 'History' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Meal History' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Saved Meals' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Plan Request' })).not.toBeInTheDocument()
  })

  it('never calls the network on first render', () => {
    render(<App />)
    expect(axios.get).not.toHaveBeenCalled()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('fires axios.post to /generate-meal-plan when the meal plan form is submitted', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.type(screen.getByLabelText(/Craving Input/i), 'High-protein burger')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/generate-meal-plan'),
      expect.objectContaining({ craving: 'High-protein burger' }),
    )
  })

  it('renders the error banner when axios.post rejects', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Backend exploded' } } })
    const user = userEvent.setup()
    render(<App />)
    await user.type(screen.getByLabelText(/Craving Input/i), 'High-protein burger')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('Backend exploded')).toBeInTheDocument()
  })

  it('renders part of the returned plan when axios.post resolves', async () => {
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
    render(<App />)
    await user.type(screen.getByLabelText(/Craving Input/i), 'High-protein burger')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))

    expect(await screen.findByText('Grilled Chicken Bowl')).toBeInTheDocument()
  })
})
