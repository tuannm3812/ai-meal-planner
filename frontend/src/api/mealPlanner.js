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
