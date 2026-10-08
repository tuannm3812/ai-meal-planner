import { useState } from 'react'

import { fetchMealPlans, fetchSavedMeals } from '../../api/mealPlanner'
import { formatDateTime, formatMacro } from '../../lib/format'
import ErrorBanner from '../../components/ui/ErrorBanner'
import InputField from '../../components/ui/InputField'
import SectionCard from '../../components/ui/SectionCard'

function HistoryTab() {
  const [userId, setUserId] = useState('user_123')
  const [limit, setLimit] = useState(10)
  const [mealHistory, setMealHistory] = useState(null)
  const [savedMeals, setSavedMeals] = useState(null)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [isLoadingSaved, setIsLoadingSaved] = useState(false)
  const [error, setError] = useState('')

  const loadHistory = async () => {
    setError('')
    setIsLoadingHistory(true)
    try {
      const data = await fetchMealPlans(userId.trim(), limit)
      setMealHistory(data)
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          'Could not load meal history. Check that the FastAPI backend is running on port 8000.',
      )
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const loadSavedMeals = async () => {
    setError('')
    setIsLoadingSaved(true)
    try {
      const data = await fetchSavedMeals(userId.trim(), limit)
      setSavedMeals(data)
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          'Could not load saved meals. Check that the FastAPI backend is running on port 8000.',
      )
    } finally {
      setIsLoadingSaved(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <aside className="rounded-2xl border border-gray-100 bg-white p-6 shadow-md lg:sticky lg:top-6 lg:self-start">
        <h2 className="text-lg font-semibold text-gray-900">History</h2>
        <p className="mt-1 text-sm leading-6 text-gray-500">
          Look up meal plans and saved meals for a user.
        </p>

        <div className="mt-6 space-y-5">
          <InputField label="User ID" onChange={(event) => setUserId(event.target.value)} value={userId} />
          <InputField
            helperText="Maximum records to fetch per list."
            label="Limit"
            max={50}
            min={1}
            onChange={(event) => setLimit(Number(event.target.value))}
            type="number"
            value={limit}
          />

          <button
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-colors duration-200 hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            disabled={!userId.trim() || isLoadingHistory}
            onClick={loadHistory}
            type="button"
          >
            {isLoadingHistory && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            )}
            {isLoadingHistory ? 'Loading history...' : 'Load meal history'}
          </button>

          <button
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-emerald-200 bg-white px-4 py-3 text-sm font-semibold text-emerald-700 shadow-sm transition-colors duration-200 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:border-gray-200 disabled:text-gray-400"
            disabled={!userId.trim() || isLoadingSaved}
            onClick={loadSavedMeals}
            type="button"
          >
            {isLoadingSaved && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
            )}
            {isLoadingSaved ? 'Loading saved meals...' : 'Load saved meals'}
          </button>
        </div>

        {error && <div className="mt-5"><ErrorBanner>{error}</ErrorBanner></div>}
      </aside>

      <div className="grid gap-6">
        <SectionCard eyebrow="Records" title="Meal History">
          {!mealHistory && (
            <p className="py-8 text-center text-sm text-gray-500">
              {isLoadingHistory ? 'Loading meal history...' : 'Load meal history to see past plans.'}
            </p>
          )}
          {mealHistory && mealHistory.items.length === 0 && (
            <p className="py-8 text-center text-sm text-gray-500">
              No meal history yet — generate a plan from the Meal Plan tab first.
            </p>
          )}
          {mealHistory && mealHistory.items.length > 0 && (
            <div className="divide-y divide-gray-100">
              {mealHistory.items.map((item, index) => (
                <div
                  className="flex items-center justify-between gap-4 py-4 transition-colors duration-150 hover:bg-gray-50"
                  key={item.request_id || index}
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-gray-900">
                      {item.meal_plan?.meal_definition?.structured_meal_name || 'Unnamed meal'}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">{formatDateTime(item.saved_at)}</p>
                  </div>
                  <p className="shrink-0 text-sm font-semibold text-gray-900">
                    {formatMacro(item.nutrition?.total_calories, ' kcal')}
                  </p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard eyebrow="Records" title="Saved Meals">
          {!savedMeals && (
            <p className="py-8 text-center text-sm text-gray-500">
              {isLoadingSaved ? 'Loading saved meals...' : 'Load saved meals to see feedback history.'}
            </p>
          )}
          {savedMeals && savedMeals.items.length === 0 && (
            <p className="py-8 text-center text-sm text-gray-500">
              No saved meals yet — mark a meal as saved from the Meal Plan tab.
            </p>
          )}
          {savedMeals && savedMeals.items.length > 0 && (
            <div className="divide-y divide-gray-100">
              {savedMeals.items.map((item, index) => (
                <div
                  className="flex items-center justify-between gap-4 py-4 transition-colors duration-150 hover:bg-gray-50"
                  key={item.request_id || index}
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-gray-900">{item.meal_name}</p>
                    <p className="mt-1 text-xs text-gray-500">{formatDateTime(item.saved_at)}</p>
                  </div>
                  <p className="shrink-0 text-sm font-semibold text-gray-900">
                    {item.rating ? `${item.rating} / 5` : item.liked ? 'Liked' : 'No rating'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  )
}

export default HistoryTab
