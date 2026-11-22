import { describe, expect, it } from 'vitest'

import { runnersUp } from './runnersUp'
import { SAMPLE_PLAN } from './samplePlan'

const withCandidates = (candidates, selected = 'chicken_fried_rice') => ({
  meal_plan: {
    meal_definition: { structured_meal_name: 'Chicken Fried Rice' },
    retrieval: { selected_meal_id: selected, candidates },
  },
})

describe('runnersUp', () => {
  it('leaves out the served meal and keeps rank order', () => {
    const plan = withCandidates([
      { meal_id: 'soup', name: 'Chicken Vegetable Soup Bowl', rank: 3 },
      { meal_id: 'chicken_fried_rice', name: 'Chicken Fried Rice', rank: 1 },
      { meal_id: 'tofu', name: 'Tofu Fried Rice', rank: 2 },
    ])
    expect(runnersUp(plan).map((meal) => meal.name)).toEqual([
      'Tofu Fried Rice',
      'Chicken Vegetable Soup Bowl',
    ])
  })

  it('caps the list', () => {
    const many = Array.from({ length: 6 }, (_, index) => ({ meal_id: `m${index}`, name: `Meal ${index}`, rank: index + 2 }))
    expect(runnersUp(withCandidates(many))).toHaveLength(3)
    expect(runnersUp(withCandidates(many), 1)).toHaveLength(1)
  })

  it('returns nothing without a retrieval', () => {
    expect(runnersUp(null)).toEqual([])
    expect(runnersUp({ meal_plan: {} })).toEqual([])
  })

  it('reads the real response shape', () => {
    expect(Array.isArray(runnersUp(SAMPLE_PLAN))).toBe(true)
  })
})
