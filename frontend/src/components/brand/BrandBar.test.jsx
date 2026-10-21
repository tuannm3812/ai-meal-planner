import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import BrandBar from './BrandBar'

describe('BrandBar', () => {
  it('names the product and keeps the mark out of the accessibility tree', () => {
    const { container } = render(<BrandBar />)
    expect(screen.getByText('AI Meal Planner')).toBeInTheDocument()
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
    expect(container.querySelector('img')).toHaveAttribute('alt', '')
  })
})
