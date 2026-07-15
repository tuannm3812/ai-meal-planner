import axios from 'axios'
import { useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
  }).format(Number(value || 0))

const formatMacro = (value, unit) => `${Number(value || 0).toFixed(1)}${unit}`

const formatDateTime = (value) => {
  if (!value) return 'Unknown time'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleString('en-AU', { dateStyle: 'medium', timeStyle: 'short' })
}

const parseCommaList = (value) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

const macroCards = [
  { key: 'total_calories', label: 'Calories', unit: ' kcal', dot: 'bg-amber-400' },
  { key: 'total_protein', label: 'Protein', unit: 'g', dot: 'bg-sky-500' },
  { key: 'total_carbs', label: 'Carbs', unit: 'g', dot: 'bg-violet-500' },
  { key: 'total_fat', label: 'Fat', unit: 'g', dot: 'bg-rose-500' },
]

const TABS = [
  { id: 'meal', label: 'Meal Plan' },
  { id: 'calories', label: 'Calories' },
  { id: 'history', label: 'History' },
]

function SparkleIcon({ className = 'h-6 w-6' }) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9L12 3z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
      <path
        d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
    </svg>
  )
}

function InputField({ helperText, label, ...inputProps }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-900">{label}</span>
      <input
        className="mt-2 w-full rounded-lg border border-gray-200 bg-white px-3.5 py-2.5 text-sm text-gray-900 shadow-sm outline-none transition-all duration-200 placeholder:text-gray-400 focus:border-transparent focus:ring-2 focus:ring-emerald-500"
        {...inputProps}
      />
      {helperText && <span className="mt-1.5 block text-xs leading-5 text-gray-500">{helperText}</span>}
    </label>
  )
}

function SelectField({ helperText, label, options, ...selectProps }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-900">{label}</span>
      <select
        className="mt-2 w-full rounded-lg border border-gray-200 bg-white px-3.5 py-2.5 text-sm text-gray-900 shadow-sm outline-none transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-emerald-500"
        {...selectProps}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {helperText && <span className="mt-1.5 block text-xs leading-5 text-gray-500">{helperText}</span>}
    </label>
  )
}

function StatCard({ dot, label, value }) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
        <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{label}</p>
      </div>
      <p className="mt-3 text-2xl font-bold tracking-tight text-gray-900">{value}</p>
    </div>
  )
}

function SectionCard({ eyebrow, title, children, className = '' }) {
  return (
    <section className={`rounded-2xl border border-gray-100 bg-white p-6 shadow-sm ${className}`}>
      <div>
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
            {eyebrow}
          </p>
        )}
        <h2 className="mt-1 text-lg font-semibold text-gray-900">{title}</h2>
      </div>
      <div className="mt-5">{children}</div>
    </section>
  )
}

function EmptyState({ isLoading, loadingTitle, loadingBody, idleTitle, idleBody }) {
  return (
    <section className="flex min-h-[420px] items-center justify-center rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
      <div className="mx-auto max-w-md text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 shadow-sm">
          {isLoading ? (
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
          ) : (
            <SparkleIcon />
          )}
        </div>
        <h2 className="mt-5 text-xl font-semibold text-gray-900">
          {isLoading ? loadingTitle : idleTitle}
        </h2>
        <p className="mt-3 text-sm leading-6 text-gray-500">{isLoading ? loadingBody : idleBody}</p>
      </div>
    </section>
  )
}

function SuccessBanner({ children }) {
  return (
    <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-3 text-sm leading-6 text-emerald-700 shadow-sm">
      {children}
    </div>
  )
}

function ErrorBanner({ children }) {
  return (
    <div className="rounded-xl border border-red-100 bg-red-50 p-3 text-sm leading-6 text-red-700 shadow-sm">
      {children}
    </div>
  )
}

function SubmitButton({ isLoading, idleLabel, loadingLabel, disabled }) {
  return (
    <button
      className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-colors duration-200 hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-gray-300"
      disabled={disabled}
      type="submit"
    >
      {isLoading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
      )}
      {isLoading ? loadingLabel : idleLabel}
    </button>
  )
}

function TabBar({ activeTab, onChange }) {
  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-gray-100 bg-white p-1 shadow-sm">
      {TABS.map((tab) => (
        <button
          className={`rounded-full px-4 py-2 text-sm font-medium transition-colors duration-150 ${
            activeTab === tab.id
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
          }`}
          key={tab.id}
          onClick={() => onChange(tab.id)}
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

function MealPlanTab() {
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
    setMealPlan(null)
    setIsLoading(true)

    try {
      const { data } = await axios.post(`${API_BASE_URL}/generate-meal-plan`, {
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

const GOAL_OPTIONS = [
  { value: 'maintain', label: 'Maintain' },
  { value: 'weight_loss', label: 'Weight loss' },
  { value: 'muscle_gain', label: 'Muscle gain' },
]

const SEX_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
]

function CaloriesTab() {
  const [age, setAge] = useState(28)
  const [sex, setSex] = useState('male')
  const [heightCm, setHeightCm] = useState(180)
  const [weightKg, setWeightKg] = useState(80)
  const [activityMultiplier, setActivityMultiplier] = useState(1.55)
  const [durationMinutes, setDurationMinutes] = useState(30)
  const [heartRateBpm, setHeartRateBpm] = useState(100)
  const [bodyTempC, setBodyTempC] = useState(37)
  const [goal, setGoal] = useState('maintain')
  const [healthConditionsInput, setHealthConditionsInput] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setResult(null)
    setIsLoading(true)

    try {
      const { data } = await axios.post(`${API_BASE_URL}/calorie-expenditure/predict`, {
        age: Number(age),
        sex,
        height_cm: Number(heightCm),
        weight_kg: Number(weightKg),
        activity_multiplier: Number(activityMultiplier),
        duration_minutes: Number(durationMinutes),
        heart_rate_bpm: Number(heartRateBpm),
        body_temp_c: Number(bodyTempC),
        goal,
        health_conditions: parseCommaList(healthConditionsInput),
      })
      setResult(data)
    } catch (requestError) {
      const message =
        requestError.response?.data?.detail ||
        'Could not predict calorie expenditure. Check that the FastAPI backend is running on port 8000.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <aside className="rounded-2xl border border-gray-100 bg-white p-6 shadow-md lg:sticky lg:top-6 lg:self-start">
        <h2 className="text-lg font-semibold text-gray-900">Calorie Expenditure</h2>
        <p className="mt-1 text-sm leading-6 text-gray-500">
          Calls the promoted Kaggle calorie model artifact.
        </p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Age"
              max={120}
              min={1}
              onChange={(event) => setAge(event.target.value)}
              type="number"
              value={age}
            />
            <SelectField label="Sex" onChange={(event) => setSex(event.target.value)} options={SEX_OPTIONS} value={sex} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Height (cm)"
              max={260}
              min={80}
              onChange={(event) => setHeightCm(event.target.value)}
              type="number"
              value={heightCm}
            />
            <InputField
              label="Weight (kg)"
              max={350}
              min={20}
              onChange={(event) => setWeightKg(event.target.value)}
              type="number"
              value={weightKg}
            />
          </div>
          <InputField
            helperText="Typical values: 1.2 sedentary, 1.375 light, 1.55 moderate, 1.725 very active, 1.9 extra active."
            label="Activity multiplier"
            max={2.5}
            min={1.0}
            onChange={(event) => setActivityMultiplier(event.target.value)}
            step={0.025}
            type="number"
            value={activityMultiplier}
          />
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Duration (min)"
              max={600}
              min={1}
              onChange={(event) => setDurationMinutes(event.target.value)}
              type="number"
              value={durationMinutes}
            />
            <InputField
              label="Heart rate (bpm)"
              max={240}
              min={20}
              onChange={(event) => setHeartRateBpm(event.target.value)}
              type="number"
              value={heartRateBpm}
            />
          </div>
          <InputField
            label="Body temp (C)"
            max={45}
            min={30}
            onChange={(event) => setBodyTempC(event.target.value)}
            step={0.1}
            type="number"
            value={bodyTempC}
          />
          <SelectField label="Goal" onChange={(event) => setGoal(event.target.value)} options={GOAL_OPTIONS} value={goal} />
          <InputField
            helperText="Comma separated, e.g. 'diabetes, hypertension'."
            label="Health conditions"
            onChange={(event) => setHealthConditionsInput(event.target.value)}
            value={healthConditionsInput}
          />

          <SubmitButton
            disabled={isLoading}
            idleLabel="Predict Expenditure"
            isLoading={isLoading}
            loadingLabel="Predicting..."
          />
        </form>

        {error && <div className="mt-5"><ErrorBanner>{error}</ErrorBanner></div>}
      </aside>

      <div className="grid gap-6">
        {!result && (
          <EmptyState
            idleBody="Fill in the biometrics on the left to estimate daily calorie expenditure and a meal budget."
            idleTitle="Predict your calorie expenditure"
            isLoading={isLoading}
            loadingBody="Running the calorie forecasting model."
            loadingTitle="Predicting expenditure"
          />
        )}

        {result && (
          <>
            <SuccessBanner>Calorie expenditure predicted using {result.model_version}.</SuccessBanner>

            <SectionCard eyebrow="Forecast" title="Calorie Expenditure">
              <div className="grid gap-4 sm:grid-cols-3">
                <StatCard
                  dot="bg-amber-400"
                  label="Daily expenditure"
                  value={`${Number(result.estimated_daily_expenditure_kcal).toLocaleString()} kcal`}
                />
                <StatCard
                  dot="bg-sky-500"
                  label="Meal budget"
                  value={`${Number(result.meal_calorie_budget_kcal).toLocaleString()} kcal`}
                />
                <StatCard
                  dot="bg-violet-500"
                  label="Confidence"
                  value={`${Math.round(result.confidence * 100)}%`}
                />
              </div>
            </SectionCard>

            {result.warnings?.length > 0 && (
              <SectionCard eyebrow="Notes" title="Warnings">
                <ul className="space-y-2 text-sm text-gray-600">
                  {result.warnings.map((warning) => (
                    <li className="rounded-lg bg-amber-50 px-3 py-2 text-amber-800" key={warning}>
                      {warning}
                    </li>
                  ))}
                </ul>
              </SectionCard>
            )}
          </>
        )}
      </div>
    </div>
  )
}

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
      const { data } = await axios.get(`${API_BASE_URL}/meal-plans/${userId.trim()}`, {
        params: { limit },
      })
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
      const { data } = await axios.get(`${API_BASE_URL}/saved-meals/${userId.trim()}`, {
        params: { limit },
      })
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

function App() {
  const [activeTab, setActiveTab] = useState('meal')

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8 text-gray-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-7">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
              Multi-Agent Meal Planner
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl">
              Meal planning dashboard
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-gray-500">
              Generate a structured meal, verified nutrition macros, and a grocery receipt
              from a single craving, predict calorie expenditure, and review history.
            </p>
          </div>
          <div className="rounded-xl border border-gray-100 bg-white px-4 py-3 text-xs text-gray-500 shadow-sm">
            API target <span className="ml-1 font-medium text-gray-900">{API_BASE_URL}</span>
          </div>
        </header>

        <TabBar activeTab={activeTab} onChange={setActiveTab} />

        {activeTab === 'meal' && <MealPlanTab />}
        {activeTab === 'calories' && <CaloriesTab />}
        {activeTab === 'history' && <HistoryTab />}
      </div>
    </main>
  )
}

export default App
