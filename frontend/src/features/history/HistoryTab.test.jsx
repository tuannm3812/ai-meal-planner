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

import HistoryTab from './HistoryTab'

describe('HistoryTab error text', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows its own fallback sentence when meal history fails with no response', async () => {
    // The only branch App.test.jsx does not cover: a rejection with no
    // `response` at all. This sentence is not routed through useAsyncRequest,
    // so it stays exactly as it was before the move.
    axios.get.mockRejectedValueOnce(new Error('Network Error'))
    const user = userEvent.setup()
    render(<HistoryTab />)

    await user.click(screen.getByRole('button', { name: 'Load meal history' }))

    expect(
      await screen.findByText(
        'Could not load meal history. Check that the FastAPI backend is running on port 8000.',
      ),
    ).toBeInTheDocument()
  })

  it('shows its own fallback sentence when saved meals fails with no response', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network Error'))
    const user = userEvent.setup()
    render(<HistoryTab />)

    await user.click(screen.getByRole('button', { name: 'Load saved meals' }))

    expect(
      await screen.findByText(
        'Could not load saved meals. Check that the FastAPI backend is running on port 8000.',
      ),
    ).toBeInTheDocument()
  })

  it("still prefers the backend's detail when there is one", async () => {
    axios.get.mockRejectedValueOnce({ response: { data: { detail: 'User not found' } } })
    const user = userEvent.setup()
    render(<HistoryTab />)

    await user.click(screen.getByRole('button', { name: 'Load meal history' }))

    expect(await screen.findByText('User not found')).toBeInTheDocument()
  })
})
