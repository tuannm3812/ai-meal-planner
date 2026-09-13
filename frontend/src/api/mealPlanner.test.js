import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { ok: 'get' } })),
    post: vi.fn(() => Promise.resolve({ data: { ok: 'post' } })),
  },
}))

import axios from 'axios'

import { API_BASE_URL } from './client'
import {
  fetchMealPlans,
  fetchSavedMeals,
  generateMealPlan,
  predictCalorieExpenditure,
} from './mealPlanner'

describe('mealPlanner', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('posts a meal plan request to the right URL and returns the body', async () => {
    const body = await generateMealPlan({ craving: 'pasta' })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/generate-meal-plan`,
      { craving: 'pasta' },
    )
    expect(body).toEqual({ ok: 'post' })
  })

  it('posts a calorie prediction to the right URL', async () => {
    await predictCalorieExpenditure({ age: 28 })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/calorie-expenditure/predict`,
      { age: 28 },
    )
  })

  it('gets meal plans for a user with the limit as a query param', async () => {
    await fetchMealPlans('user_123', 10)
    expect(axios.get).toHaveBeenCalledWith(
      `${API_BASE_URL}/meal-plans/user_123`,
      { params: { limit: 10 } },
    )
  })

  it('gets saved meals for a user with the limit as a query param', async () => {
    await fetchSavedMeals('user_123', 5)
    expect(axios.get).toHaveBeenCalledWith(
      `${API_BASE_URL}/saved-meals/user_123`,
      { params: { limit: 5 } },
    )
  })
})
