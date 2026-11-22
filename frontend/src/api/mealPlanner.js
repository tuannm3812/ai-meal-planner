import axios from 'axios'

import { API_BASE_URL } from './client'

export async function generateMealPlan(payload) {
  const { data } = await axios.post(`${API_BASE_URL}/generate-meal-plan`, payload)
  return data
}

export async function predictCalorieExpenditure(payload) {
  const { data } = await axios.post(`${API_BASE_URL}/calorie-expenditure/predict`, payload)
  return data
}

export async function fetchMealPlans(userId, limit) {
  const { data } = await axios.get(`${API_BASE_URL}/meal-plans/${userId}`, {
    params: { limit },
  })
  return data
}

export async function fetchSavedMeals(userId, limit) {
  const { data } = await axios.get(`${API_BASE_URL}/saved-meals/${userId}`, {
    params: { limit },
  })
  return data
}

export async function fetchHealth() {
  const { data } = await axios.get(`${API_BASE_URL}/health`)
  return data
}

export async function fetchMealFeedback(userId, limit) {
  const { data } = await axios.get(`${API_BASE_URL}/meal-feedback/${userId}`, {
    params: { limit },
  })
  return data
}

// Save or rate a plan. Feedback is append-only on the server.
export async function sendFeedback(payload) {
  const { data } = await axios.post(`${API_BASE_URL}/meal-feedback`, payload)
  return data
}
