import { useEffect, useState } from 'react'

import { fetchMealPlans, fetchSavedMeals } from '../../api/mealPlanner'
import { isNotImplemented } from '../plan/feedback'
import { dedupeSaved, pastMeals } from './meals'

const LOAD_ERROR =
  'Could not load your meals. Check your connection and try again.'

// Saved meals and past plans for this device's user ID. A hosted API answers
// 501 (G6), which is a state to explain, not an error.
export function useMealLists(userId, { enabled = true, limit = 50 } = {}) {
  const key = enabled && userId ? `${userId}:${limit}` : null
  const [state, setState] = useState({ key: null })

  useEffect(() => {
    if (!key) return undefined
    let active = true
    Promise.all([fetchSavedMeals(userId, limit), fetchMealPlans(userId, limit)])
      .then(([saved, history]) => {
        if (!active) return
        const raw = history?.items ?? []
        const byRequest = new Map(pastMeals(raw).map((meal) => [meal.requestId, meal]))
        setState({
          key,
          status: 'ready',
          // A saved meal shows its plan's numbers when the plan is in history.
          saved: dedupeSaved(saved?.items).map(
            (item) =>
              byRequest.get(item.request_id) ?? {
                requestId: item.request_id,
                name: item.meal_name,
                craving: null,
                kcal: null,
                split: null,
                dish: null,
              },
          ),
          history: pastMeals(raw),
          raw,
          error: '',
        })
      })
      .catch((error) => {
        if (!active) return
        setState({
          key,
          status: isNotImplemented(error) ? 'hosted' : 'error',
          saved: [],
          history: [],
          raw: [],
          error: isNotImplemented(error) ? '' : error?.response?.data?.detail || LOAD_ERROR,
        })
      })
    return () => {
      active = false
    }
  }, [key, userId, limit])

  // Until this key's answer arrives, the lists are loading (or idle when off).
  if (state.key === key && key) return state
  return { key, status: key ? 'loading' : 'idle', saved: [], history: [], raw: [], error: '' }
}
