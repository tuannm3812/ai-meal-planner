import { useMemo, useState } from 'react'

import { generateMealPlan } from '../../api/mealPlanner'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import EmptyState from '../../components/ui/EmptyState'
import ErrorBanner from '../../components/ui/ErrorBanner'
import InputField from '../../components/ui/InputField'
import SubmitButton from '../../components/ui/SubmitButton'
import MealPlanResult from './MealPlanResult'

function MealPlanTab() {
  const [craving, setCraving] = useState('')
  const [userId, setUserId] = useState('user_123')
  const [location, setLocation] = useState('Earlwood, NSW')
  const {
    data: mealPlan,
    error,
    isLoading,
    run: requestMealPlan,
    reset: clearMealPlan,
  } = useAsyncRequest(
    generateMealPlan,
    'Could not generate a meal plan. Check that the FastAPI backend is running on port 8000.',
  )

  const mealDefinition = mealPlan?.meal_plan?.meal_definition
  const nutrition = mealPlan?.nutrition
  const shopping = mealPlan?.shopping_list
  const ingredients = mealDefinition?.ingredients || []
  const shoppingItems = shopping?.shopping_list || []

  const canSubmit = useMemo(
    () => craving.trim() && userId.trim() && location.trim() && !isLoading,
    [craving, userId, location, isLoading],
  )

  const handleSubmit = async (event) => {
    event.preventDefault()
    clearMealPlan()
    await requestMealPlan({
      user_id: userId.trim(),
      craving: craving.trim(),
      location: location.trim(),
    })
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <aside className="rounded-2xl border border-gray-100 bg-white p-6 shadow-md lg:sticky lg:top-6 lg:self-start">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Plan Request</h2>
            <p className="mt-1 text-sm leading-6 text-gray-500">
              Define the prompt and user context for the workflow.
            </p>
          </div>
          <div className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
            Live
          </div>
        </div>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <InputField
            helperText="Try 'Spicy noodles' or 'High-protein breakfast'."
            label="Craving Input"
            placeholder="High-protein burger"
            value={craving}
            onChange={(event) => setCraving(event.target.value)}
          />

          <InputField
            helperText="Used to retrieve profile preferences and dietary context."
            label="User ID"
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
          />

          <InputField
            helperText="Used to localize supermarket recommendations."
            label="Location"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
          />

          <SubmitButton
            disabled={!canSubmit}
            idleLabel="Generate Meal Plan"
            isLoading={isLoading}
            loadingLabel="Orchestrating Agents..."
          />
        </form>

        {error && <div className="mt-5"><ErrorBanner>{error}</ErrorBanner></div>}
      </aside>

      <div className="grid gap-6">
        {!mealPlan && (
          <EmptyState
            idleBody="Enter a craving to generate your personalized meal plan, nutrition macros, and grocery list."
            idleTitle="Enter a craving to generate your plan"
            isLoading={isLoading}
            loadingBody="The meal, nutrition, and grocery agents are coordinating a personalized result."
            loadingTitle="Orchestrating your agents"
          />
        )}

        {mealPlan && (
          <MealPlanResult
            craving={craving.trim()}
            ingredients={ingredients}
            location={location}
            mealDefinition={mealDefinition}
            nutrition={nutrition}
            shopping={shopping}
            shoppingItems={shoppingItems}
          />
        )}
      </div>
    </div>
  )
}

export default MealPlanTab
