import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

// The backend's corpus itself, so the page's recipe count can never drift.
import corpus from '../../../data/meal_corpus/meals.json'
import { renderApp } from '../test/renderApp'

describe('WelcomePage', () => {
  it('opens a first visit on the landing page, with the form below', () => {
    renderApp()
    expect(screen.getByRole('heading', { level: 1, name: /Say what you crave/ })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Get started' })).toHaveAttribute('href', '#get-started')
    expect(screen.getByRole('heading', { level: 2, name: 'How it works' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Tell us about you' })).toBeInTheDocument()
    expect(screen.getByText(/A planning aid, not medical advice/)).toBeInTheDocument()
  })

  it('states the menu size the corpus really has', () => {
    renderApp()
    expect(screen.getByText(`${corpus.length} tested recipes. Here are a few to try.`)).toBeInTheDocument()
  })

  it('still says where the details go', () => {
    renderApp()
    expect(screen.getByText(/the server keeps a history of the plans it makes/)).toBeInTheDocument()
  })
})
