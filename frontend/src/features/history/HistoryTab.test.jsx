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
    // G6: the tab reads /health on mount, so that call takes the first queued get.
    axios.get.mockResolvedValueOnce({ data: { services: { hosted_mode: false } } })
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
    // G6: the tab reads /health on mount, so that call takes the first queued get.
    axios.get.mockResolvedValueOnce({ data: { services: { hosted_mode: false } } })
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
    // G6: the tab reads /health on mount, so that call takes the first queued get.
    axios.get.mockResolvedValueOnce({ data: { services: { hosted_mode: false } } })
    axios.get.mockRejectedValueOnce({ response: { data: { detail: 'User not found' } } })
    const user = userEvent.setup()
    render(<HistoryTab />)

    await user.click(screen.getByRole('button', { name: 'Load meal history' }))

    expect(await screen.findByText('User not found')).toBeInTheDocument()
  })

  it('hides the history views when /health reports a hosted deployment', async () => {
    // G6: the hosted API refuses history with 501, so the tab must not offer it.
    axios.get.mockResolvedValueOnce({ data: { services: { hosted_mode: true } } })
    render(<HistoryTab />)

    expect(await screen.findByText('History is disabled')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Meal History' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Load meal history' })).not.toBeInTheDocument()
  })

  it('keeps history and labels it non-persistent when not hosted', async () => {
    axios.get.mockResolvedValueOnce({ data: { services: { hosted_mode: false } } })
    render(<HistoryTab />)

    expect(screen.getByText(/History is not persisted/)).toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: 'Meal History' })).toBeInTheDocument()
    expect(screen.queryByText('History is disabled')).not.toBeInTheDocument()
  })
})
