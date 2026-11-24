import { beforeEach, describe, expect, it, vi } from 'vitest'

// DEC-43: with accounts on, every call carries the ID token and acts for the uid.
vi.mock('../auth/firebase', () => ({
  apiIdentity: vi.fn(() =>
    Promise.resolve({ headers: { Authorization: 'Bearer tok' }, uid: 'uid-1' }),
  ),
}))

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { ok: 'get' } })),
    post: vi.fn(() => Promise.resolve({ data: { ok: 'post' } })),
    put: vi.fn(() => Promise.resolve({ data: { ok: 'put' } })),
    delete: vi.fn(() => Promise.resolve({ data: { ok: 'delete' } })),
  },
}))

import axios from 'axios'

import { API_BASE_URL } from './client'
import {
  deleteAccountData,
  fetchAccountProfile,
  fetchMealPlans,
  generateMealPlan,
  predictCalorieExpenditure,
  saveAccountProfile,
  sendFeedback,
} from './mealPlanner'

const AUTH = { headers: { Authorization: 'Bearer tok' } }

describe('mealPlanner with accounts on', () => {
  beforeEach(() => vi.clearAllMocks())

  it('plans as the signed-in uid, with the token', async () => {
    await generateMealPlan({ user_id: 'web-device', craving: 'pasta' })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/generate-meal-plan`,
      { user_id: 'uid-1', craving: 'pasta' },
      AUTH,
    )
  })

  it('adds no user_id to a body that has none', async () => {
    await predictCalorieExpenditure({ age: 28 })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/calorie-expenditure/predict`,
      { age: 28 },
      AUTH,
    )
  })

  it('reads history at the uid, never the device ID', async () => {
    await fetchMealPlans('web-device', 5)
    expect(axios.get).toHaveBeenCalledWith(`${API_BASE_URL}/meal-plans/uid-1`, {
      params: { limit: 5 },
      ...AUTH,
    })
  })

  it('sends feedback as the uid', async () => {
    await sendFeedback({ user_id: 'web-device', request_id: 'r1', saved: true })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/meal-feedback`,
      { user_id: 'uid-1', request_id: 'r1', saved: true },
      AUTH,
    )
  })

  it('reads, saves and deletes the account', async () => {
    await fetchAccountProfile()
    await saveAccountProfile({ goal: 'lose' }, 'Ashfield')
    await deleteAccountData()
    expect(axios.get).toHaveBeenCalledWith(`${API_BASE_URL}/me/profile`, AUTH)
    expect(axios.put).toHaveBeenCalledWith(
      `${API_BASE_URL}/me/profile`,
      { profile: { goal: 'lose' }, location: 'Ashfield' },
      AUTH,
    )
    expect(axios.delete).toHaveBeenCalledWith(`${API_BASE_URL}/me`, AUTH)
  })

  it('reads a missing account profile as null', async () => {
    axios.get.mockRejectedValueOnce({ response: { status: 404 } })
    expect(await fetchAccountProfile()).toBeNull()
  })

  it('passes on any other account error', async () => {
    axios.get.mockRejectedValueOnce({ response: { status: 500 } })
    await expect(fetchAccountProfile()).rejects.toEqual({ response: { status: 500 } })
  })
})
