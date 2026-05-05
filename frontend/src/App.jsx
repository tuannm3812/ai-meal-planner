import axios from 'axios'
import { useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_URL = `${API_BASE_URL}/generate-meal-plan`

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
  }).format(Number(value || 0))

const formatMacro = (value, unit) => `${Number(value || 0).toFixed(1)}${unit}`

function StatCard({ label, value, tone }) {
  return (
    <div className={`rounded-lg border p-4 ${tone}`}>
      <p className="text-sm font-medium text-slate-600">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
    </div>
  )
}

function SectionCard({ title, children, className = '' }) {
  return (
    <section className={`rounded-lg border border-slate-200 bg-white p-6 shadow-sm ${className}`}>
      <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      <div className="mt-5">{children}</div>
    </section>
  )
}

function App() {
  const [craving, setCraving] = useState('')
  const [userId, setUserId] = useState('user_123')
  const [location, setLocation] = useState('Earlwood, NSW')
  const [mealPlan, setMealPlan] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

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
    setError('')
    setIsLoading(true)

    try {
      const { data } = await axios.post(API_URL, {
        user_id: userId.trim(),
        craving: craving.trim(),
        location: location.trim(),
      })

      setMealPlan(data)
    } catch (requestError) {
      const message =
        requestError.response?.data?.detail ||
        'Could not generate a meal plan. Check that the FastAPI backend is running on port 8000.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-6 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
            Multi-Agent Meal Planner
          </p>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-950 sm:text-4xl">
                Meal planning dashboard
              </h1>
              <p className="mt-2 max-w-2xl text-slate-600">
                Send a craving to the orchestrator and review the generated recipe,
                nutrition totals, and supermarket estimate in one place.
              </p>
            </div>
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
              API target: <span className="font-semibold">{API_URL}</span>
            </div>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
          <aside className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm lg:sticky lg:top-6 lg:self-start">
            <h2 className="text-lg font-semibold text-slate-950">Plan Request</h2>
            <form className="mt-5 space-y-5" onSubmit={handleSubmit}>
              <label className="block">
                <span className="text-sm font-medium text-slate-700">Craving Input</span>
                <input
                  className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-950 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
                  placeholder="High-protein burger"
                  value={craving}
                  onChange={(event) => setCraving(event.target.value)}
                />
              </label>

              <label className="block">
                <span className="text-sm font-medium text-slate-700">User ID</span>
                <input
                  className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-950 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                />
              </label>

              <label className="block">
                <span className="text-sm font-medium text-slate-700">Location</span>
                <input
                  className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-950 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
                  value={location}
                  onChange={(event) => setLocation(event.target.value)}
                />
              </label>

              <button
                className="flex w-full items-center justify-center gap-2 rounded-md bg-emerald-700 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
                disabled={!canSubmit}
                type="submit"
              >
                {isLoading && (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                )}
                {isLoading ? 'Generating...' : 'Generate Meal Plan'}
              </button>
            </form>

            {error && (
              <div className="mt-5 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                {error}
              </div>
            )}
          </aside>

          <div className="grid gap-6">
            {!mealPlan && !isLoading && (
              <section className="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
                <h2 className="text-xl font-semibold text-slate-950">Ready for a craving</h2>
                <p className="mx-auto mt-3 max-w-xl text-slate-600">
                  Enter a meal idea and the dashboard will populate with the orchestrator
                  response once the agents finish their work.
                </p>
              </section>
            )}

            {mealPlan && (
              <>
                <SectionCard title="Meal Overview">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-500">Structured meal</p>
                      <p className="mt-1 text-2xl font-semibold text-slate-950">
                        {mealDefinition?.structured_meal_name || 'Untitled meal'}
                      </p>
                    </div>
                    <div className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700">
                      {ingredients.length} ingredients
                    </div>
                  </div>

                  <div className="mt-6 overflow-hidden rounded-lg border border-slate-200">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-slate-50 text-slate-600">
                        <tr>
                          <th className="px-4 py-3 font-semibold">Ingredient</th>
                          <th className="px-4 py-3 text-right font-semibold">Base Quantity</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200">
                        {ingredients.map((ingredient) => (
                          <tr key={ingredient.item_name}>
                            <td className="px-4 py-3 text-slate-900">{ingredient.item_name}</td>
                            <td className="px-4 py-3 text-right text-slate-600">
                              {ingredient.base_quantity_grams}g
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </SectionCard>

                <SectionCard title="Nutrition">
                  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <StatCard
                      label="Total Calories"
                      value={formatMacro(nutrition?.total_calories, ' kcal')}
                      tone="border-amber-200 bg-amber-50"
                    />
                    <StatCard
                      label="Protein"
                      value={formatMacro(nutrition?.total_protein, 'g')}
                      tone="border-sky-200 bg-sky-50"
                    />
                    <StatCard
                      label="Carbs"
                      value={formatMacro(nutrition?.total_carbs, 'g')}
                      tone="border-violet-200 bg-violet-50"
                    />
                    <StatCard
                      label="Fat"
                      value={formatMacro(nutrition?.total_fat, 'g')}
                      tone="border-rose-200 bg-rose-50"
                    />
                  </div>
                </SectionCard>

                <SectionCard title="Supermarket">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-500">Nearest store</p>
                      <p className="mt-1 text-xl font-semibold text-slate-950">
                        {shopping?.store_details?.store_name || 'Store unavailable'}
                      </p>
                      <p className="mt-1 text-sm text-slate-600">
                        {shopping?.store_details?.address || location}
                      </p>
                    </div>
                    <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-right">
                      <p className="text-sm font-medium text-emerald-800">Estimated total</p>
                      <p className="mt-1 text-2xl font-semibold text-emerald-950">
                        {formatCurrency(shopping?.total_estimated_cost)}
                      </p>
                    </div>
                  </div>

                  <div className="mt-6 grid gap-3">
                    {shoppingItems.map((item) => (
                      <div
                        className="grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:grid-cols-[1fr_auto]"
                        key={item.store_product_name}
                      >
                        <div>
                          <p className="font-semibold text-slate-950">
                            {item.store_product_name}
                          </p>
                          <p className="mt-1 text-sm text-slate-600">
                            {item.original_item_name} - {item.category_or_aisle}
                          </p>
                        </div>
                        <p className="text-lg font-semibold text-slate-950 sm:text-right">
                          {formatCurrency(item.estimated_price)}
                        </p>
                      </div>
                    ))}
                  </div>
                </SectionCard>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

export default App
