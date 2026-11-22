import { describe, expect, it } from 'vitest'

import { SAMPLE_PLAN } from '../plan/samplePlan'
import { dedupeSaved, findPlan, pastMeals, planSummary } from './meals'

describe('meals', () => {
  it('keeps the newest saved record per plan and drops unsaved ones', () => {
    const items = [
      { request_id: 'req-a', saved: true, meal_name: 'A', saved_at: '2026-11-22T01:00:00Z' },
      { request_id: 'req-a', saved: true, meal_name: 'A', saved_at: '2026-11-22T03:00:00Z' },
      { request_id: 'req-b', saved: false, rating: 4, saved_at: '2026-11-22T04:00:00Z' },
      { request_id: 'req-c', saved: true, meal_name: 'C', saved_at: '2026-11-22T02:00:00Z' },
    ]
    expect(dedupeSaved(items).map((item) => [item.request_id, item.saved_at])).toEqual([
      ['req-a', '2026-11-22T03:00:00Z'],
      ['req-c', '2026-11-22T02:00:00Z'],
    ])
    expect(dedupeSaved(undefined)).toEqual([])
  })

  it('finds a stored plan by request ID', () => {
    const items = [{ request_id: 'req-1' }, { request_id: 'req-2' }]
    expect(findPlan(items, 'req-2')).toBe(items[1])
    expect(findPlan(items, 'nope')).toBeNull()
    expect(findPlan(null, 'req-1')).toBeNull()
  })

  it('summarises a real plan for its card', () => {
    const summary = planSummary(SAMPLE_PLAN)
    expect(summary).toMatchObject({
      requestId: 'sample-request',
      name: 'Chicken Fried Rice',
      craving: 'chicken fried rice',
      kcal: 629,
      dish: 'rice',
    })
    expect(Math.round(summary.split.protein)).toBe(27)
  })

  it('invents nothing for a sparse plan and leaves infeasible plans off the cards', () => {
    expect(planSummary({ request_id: 'r' })).toMatchObject({ name: null, kcal: null, split: null })
    const items = [
      { request_id: 'r1', plan_status: 'infeasible', meal_plan: null, saved_at: '2' },
      { ...SAMPLE_PLAN, saved_at: '1' },
    ]
    expect(pastMeals(items).map((meal) => meal.requestId)).toEqual(['sample-request'])
  })
})
