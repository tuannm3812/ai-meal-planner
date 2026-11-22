import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import DishIllustration from './DishIllustration'
import { DISH_TYPES } from './dishType'

describe('DishIllustration', () => {
  it.each(DISH_TYPES)('draws %s, hidden from assistive technology', (type) => {
    const { container } = render(<DishIllustration type={type} />)
    const svg = container.querySelector('svg')
    expect(svg).toHaveAttribute('aria-hidden', 'true')
    expect(svg).toHaveAttribute('data-dish', type)
    expect(svg.querySelectorAll('path, rect, circle, ellipse').length).toBeGreaterThan(3)
  })

  it('picks the drawing from the meal name', () => {
    const { container } = render(<DishIllustration mealName="Chicken Fried Rice" />)
    expect(container.querySelector('svg')).toHaveAttribute('data-dish', 'rice')
  })
})
