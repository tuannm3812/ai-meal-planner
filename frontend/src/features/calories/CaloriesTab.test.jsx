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

import CaloriesTab from './CaloriesTab'

describe('CaloriesTab error text', () => {
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
    render(<CaloriesTab />)

    await user.click(screen.getByRole('button', { name: 'Predict Expenditure' }))

    expect(
      await screen.findByText(
        'Could not predict calorie expenditure. Check that the FastAPI backend is running on port 8000.',
      ),
    ).toBeInTheDocument()
  })

  it("still prefers the backend's detail when there is one", async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Age out of range' } } })
    const user = userEvent.setup()
    render(<CaloriesTab />)

    await user.click(screen.getByRole('button', { name: 'Predict Expenditure' }))

    expect(await screen.findByText('Age out of range')).toBeInTheDocument()
  })
})
