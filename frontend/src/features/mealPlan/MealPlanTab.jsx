import { useMemo, useState } from 'react'

import { generateMealPlan } from '../../api/mealPlanner'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import { formatCurrency, formatMacro, macroCards } from '../../lib/format'
import EmptyState from '../../components/ui/EmptyState'
import ErrorBanner from '../../components/ui/ErrorBanner'
import InputField from '../../components/ui/InputField'
import SectionCard from '../../components/ui/SectionCard'
import StatCard from '../../components/ui/StatCard'
import SubmitButton from '../../components/ui/SubmitButton'
import SuccessBanner from '../../components/ui/SuccessBanner'

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
          <>
            <SuccessBanner>
              Meal plan generated successfully for &ldquo;{craving.trim()}&rdquo;.
            </SuccessBanner>

            <SectionCard eyebrow="Recipe" title="Meal Overview">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Structured meal</p>
                  <p className="mt-1 text-2xl font-semibold tracking-tight text-gray-900">
                    {mealDefinition?.structured_meal_name || 'Untitled meal'}
                  </p>
                </div>
                <div className="rounded-full bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-600">
                  {ingredients.length} ingredients
                </div>
              </div>

              <div className="mt-6 overflow-hidden">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="py-3 pr-4">Ingredient</th>
                      <th className="py-3 pl-4 text-right">Base Quantity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {ingredients.map((ingredient) => (
                      <tr
                        className="transition-colors duration-150 hover:bg-gray-50"
                        key={ingredient.item_name}
                      >
                        <td className="py-3.5 pr-4 font-medium text-gray-900">
                          {ingredient.item_name}
                        </td>
                        <td className="py-3.5 pl-4 text-right text-gray-500">
                          {ingredient.base_quantity_grams}g
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </SectionCard>

            <SectionCard eyebrow="Analytics" title="Nutrition">
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {macroCards.map((macro) => (
                  <StatCard
                    dot={macro.dot}
                    key={macro.key}
                    label={macro.label}
                    value={formatMacro(nutrition?.[macro.key], macro.unit)}
                  />
                ))}
              </div>
            </SectionCard>

            <SectionCard eyebrow="Grocery" title="Supermarket">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Nearest store</p>
                  <p className="mt-1 text-xl font-semibold text-gray-900">
                    {shopping?.store_details?.store_name || 'Store unavailable'}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    {shopping?.store_details?.address || location}
                  </p>
                </div>
                <div className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-right">
                  <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Estimated total
                  </p>
                  <p className="mt-1 text-2xl font-bold tracking-tight text-gray-900">
                    {formatCurrency(shopping?.total_estimated_cost)}
                  </p>
                </div>
              </div>

              <div className="mt-6 overflow-hidden rounded-xl bg-gray-50 shadow-sm">
                <div className="divide-y divide-gray-100 bg-white">
                  {shoppingItems.map((item) => (
                    <div
                      className="flex items-center justify-between gap-4 px-4 py-4 transition-colors duration-150 hover:bg-gray-50"
                      key={item.store_product_name}
                    >
                      <div className="min-w-0">
                        <p className="truncate font-medium text-gray-900">
                          {item.store_product_name}
                        </p>
                        <p className="mt-1 text-xs text-gray-500">
                          {item.original_item_name} - {item.category_or_aisle}
                        </p>
                      </div>
                      <p className="shrink-0 font-semibold text-gray-900">
                        {formatCurrency(item.estimated_price)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </SectionCard>
          </>
        )}
      </div>
    </div>
  )
}

export default MealPlanTab
