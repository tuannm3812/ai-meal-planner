import { describe, expect, it } from 'vitest'

import { VIRIDIS, donutSegments, ringFraction, sourceSegments } from './geometry'

describe('chart geometry', () => {
  it('fills the ring by served over target, capped at a full ring', () => {
    expect(ringFraction(629, 625)).toBe(1)
    expect(ringFraction(300, 600)).toBe(0.5)
    expect(ringFraction(300, null)).toBeNull()
    expect(ringFraction(300, 0)).toBeNull()
  })

  it('splits the donut circle in macro order', () => {
    const segments = donutSegments({ protein: 27, carbs: 46, fat: 27 }, 48)
    const circumference = 2 * Math.PI * 48
    expect(segments.map((segment) => segment.key)).toEqual(['protein', 'carbs', 'fat'])
    expect(segments.reduce((sum, segment) => sum + segment.length, 0)).toBeCloseTo(circumference)
    expect(segments[0].offset).toBe(-0)
    expect(segments[1].offset).toBeCloseTo(-segments[0].length)
    expect(segments[2].offset).toBeCloseTo(-(segments[0].length + segments[1].length))
    expect(donutSegments(null, 48)).toEqual([])
  })

  it('orders calorie sources largest first with ramp colours, dropping unknown kcal', () => {
    const segments = sourceSegments([
      { name: 'soy sauce', kcal: 7.9 },
      { name: 'cooked white rice', kcal: 260 },
      { name: 'water', kcal: null },
      { name: 'chicken breast', kcal: 140.2 },
    ])
    expect(segments.map((segment) => segment.name)).toEqual([
      'cooked white rice',
      'chicken breast',
      'soy sauce',
    ])
    expect(segments.map((segment) => segment.color)).toEqual(VIRIDIS.slice(0, 3))
    expect(segments.reduce((sum, segment) => sum + segment.share, 0)).toBeCloseTo(100)
    expect(sourceSegments([])).toEqual([])
  })
})
