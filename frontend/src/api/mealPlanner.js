// Deliberately not exporting an axios.create() instance here. App.test.jsx mocks the
// axios module at the top level with only `default.get` and `default.post` (no
// `create`), so a configured instance would bypass that mock and break the eight-test
// regression harness. mealPlanner.js calls the default axios export directly instead.
import axios from 'axios'

import { apiIdentity } from '../auth/firebase'
import { API_BASE_URL } from './client'

// With accounts on (DEC-43) every call carries the user's ID token, and the
// user is the token's uid: the API refuses a history path naming anyone else.
// With accounts off nothing changes, and no config argument is added.
async function identify(userId, config) {
  const { headers, uid } = await apiIdentity()
  const withHeaders = Object.keys(headers).length ? { ...config, headers } : config
  return { userId: uid ?? userId, config: withHeaders }
}

function args(config) {
  return config ? [config] : []
}

async function post(path, payload) {
  const { userId, config } = await identify(payload?.user_id)
  const body = payload && 'user_id' in payload && userId ? { ...payload, user_id: userId } : payload
  const { data } = await axios.post(`${API_BASE_URL}${path}`, body, ...args(config))
  return data
}

async function getForUser(path, userId, limit) {
  const identity = await identify(userId, { params: { limit } })
  const { data } = await axios.get(`${API_BASE_URL}${path}/${identity.userId}`, identity.config)
  return data
}

export async function generateMealPlan(payload) {
  return post('/generate-meal-plan', payload)
}

export async function predictCalorieExpenditure(payload) {
  return post('/calorie-expenditure/predict', payload)
}

export async function fetchMealPlans(userId, limit) {
  return getForUser('/meal-plans', userId, limit)
}

export async function fetchSavedMeals(userId, limit) {
  return getForUser('/saved-meals', userId, limit)
}

export async function fetchHealth() {
  const { data } = await axios.get(`${API_BASE_URL}/health`)
  return data
}

export async function fetchMealFeedback(userId, limit) {
  return getForUser('/meal-feedback', userId, limit)
}

// Save or rate a plan. Feedback is append-only on the server.
export async function sendFeedback(payload) {
  return post('/meal-feedback', payload)
}

// --- The signed-in user's account (DEC-43). Only called with accounts on. ---

// The account's saved profile, or null when it has none (404).
export async function fetchAccountProfile() {
  const { config } = await identify(null)
  try {
    const { data } = await axios.get(`${API_BASE_URL}/me/profile`, ...args(config))
    return data
  } catch (error) {
    if (error?.response?.status === 404) return null
    throw error
  }
}

export async function saveAccountProfile(profile, location) {
  const { config } = await identify(null)
  const { data } = await axios.put(
    `${API_BASE_URL}/me/profile`,
    { profile, location },
    ...args(config),
  )
  return data
}

export async function deleteAccountData() {
  const { config } = await identify(null)
  const { data } = await axios.delete(`${API_BASE_URL}/me`, ...args(config))
  return data
}
