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

import App from '../../App'

describe('Profile across tabs', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('keeps the entered details after visiting another tab', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.clear(screen.getByLabelText('Weight (kg)'))
    await user.type(screen.getByLabelText('Weight (kg)'), '82')
    await user.click(screen.getByRole('checkbox', { name: 'Peanut allergy' }))

    await user.click(screen.getByRole('button', { name: 'Calories' }))
    await user.click(screen.getByRole('button', { name: 'Meal Plan' }))

    expect(screen.getByLabelText('Weight (kg)')).toHaveValue(82)
    expect(screen.getByRole('checkbox', { name: 'Peanut allergy' })).toBeChecked()

    await user.type(screen.getByLabelText(/Craving Input/i), 'fried rice')
    await user.click(screen.getByRole('button', { name: 'Generate Meal Plan' }))
    expect(axios.post.mock.calls[0][1]).toMatchObject({
      weight_kg: 82,
      health_conditions: ['peanut allergy'],
    })
  })
})
