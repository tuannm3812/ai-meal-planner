import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'

// The backend's corpus itself, so the page's recipe count can never drift.
import corpus from '../../../data/meal_corpus/meals.json'
import { renderApp } from '../test/renderApp'

describe('WelcomePage', () => {
  it('opens a first visit on the landing page, one h1, with the form below', () => {
    renderApp()
    const h1s = screen.getAllByRole('heading', { level: 1 })
    expect(h1s).toHaveLength(1)
    expect(h1s[0]).toHaveTextContent(/Say what you crave/)
    for (const name of [
      'How it works',
      'A real menu, not made-up meals',
      'Every plan shows its working',
      'Tell us about you',
    ]) {
      expect(screen.getByRole('heading', { level: 2, name })).toBeInTheDocument()
    }
    expect(screen.getByText('A planning aid, not medical advice.')).toBeInTheDocument()
  })

  it('states the menu size the corpus really has', () => {
    renderApp()
    expect(screen.getByText(`${corpus.length} tested recipes. Here are a few to try.`)).toBeInTheDocument()
  })

  it('labels the example plan as an example', () => {
    renderApp()
    expect(screen.getByText('Example plan')).toBeInTheDocument()
    expect(screen.getByRole('img', { name: /629 kcal against a 625 kcal meal target/ })).toBeInTheDocument()
  })

  it('still says where the details go', () => {
    renderApp()
    expect(screen.getByText(/the server keeps a history of the plans it makes/)).toBeInTheDocument()
  })

  it('moves focus to the form on Get started, without a request or a URL change', async () => {
    const user = userEvent.setup()
    renderApp()
    const before = window.location.href
    await user.click(screen.getByRole('button', { name: /Get started/ }))
    expect(screen.getByRole('heading', { name: 'Tell us about you' })).toHaveFocus()
    expect(window.location.href).toBe(before)
    expect(axios.post).not.toHaveBeenCalled()
  })
})
