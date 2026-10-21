import { useMemo, useState } from 'react'

import { generateMealPlan } from '../../api/mealPlanner'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import EmptyState from '../../components/ui/EmptyState'
import ErrorBanner from '../../components/ui/ErrorBanner'
import InputField from '../../components/ui/InputField'
import SubmitButton from '../../components/ui/SubmitButton'
import CravingSuggestions from '../craving/CravingSuggestions'
import { requestErrorsFrom422, validateRequest } from '../craving/craving'
import ProfileForm from '../profile/ProfileForm'
import {
  DEFAULT_PROFILE,
  errorsForUnchangedFields,
  profileErrorsFrom422,
  profileToRequest,
  sameRequest,
  validateProfile,
} from '../profile/profile'
import MealPlanResult from './MealPlanResult'

// A 422 that names no field on screen still says what the service rejected, rather than the "is the backend running" sentence.
function describeRejection(detail) {
  return detail
    .map((item) => {
      const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null
      return field ? `${field}: ${item?.msg}` : item?.msg
    })
    .filter(Boolean)
    .join('; ')
}

// The profile is passed in by App, which outlives the tabs, so leaving this
// tab and coming back keeps the person's details. Rendered on its own (as in
// the tab's tests) it holds its own copy.
function MealPlanTab({ profile: sharedProfile, onProfileChange }) {
  const [craving, setCraving] = useState('')
  const [userId, setUserId] = useState('user_123')
  const [location, setLocation] = useState('Earlwood, NSW')
  // The profile is React state only: never the URL, never browser storage.
  const [ownProfile, setOwnProfile] = useState(DEFAULT_PROFILE)
  const profile = sharedProfile ?? ownProfile
  const setProfile = onProfileChange ?? setOwnProfile
  // What the last request was sent with. The result names this craving and
  // location, not the live inputs, and a plan made for anything else is
  // marked stale rather than shown as current.
  const [submitted, setSubmitted] = useState(null)
  const submittedProfile = submitted?.profile ?? null
  const {
    data: mealPlan,
    error,
    errorDetail,
    isLoading,
    run: requestMealPlan,
    reset: clearMealPlan,
  } = useAsyncRequest(
    generateMealPlan,
    'Could not generate a meal plan. Check that the FastAPI backend is running on port 8000.',
  )

  // G3: "infeasible" is a successful response with null meal sections.
  const isInfeasible = mealPlan?.plan_status === 'infeasible'
  const mealDefinition = mealPlan?.meal_plan?.meal_definition
  const nutrition = mealPlan?.nutrition
  const shopping = mealPlan?.shopping_list
  const ingredients = mealDefinition?.ingredients || []
  const shoppingItems = shopping?.shopping_list || []

  const profileErrors = useMemo(() => validateProfile(profile), [profile])
  const profileIsValid = Object.keys(profileErrors).length === 0
  const requestValues = { craving, location, userId }
  const requestErrors = validateRequest(requestValues)
  const requestIsValid = Object.keys(requestErrors).length === 0
  const requestEdited =
    submitted !== null &&
    (craving.trim() !== submitted.craving ||
      location.trim() !== submitted.location ||
      userId.trim() !== submitted.userId)
  const profileEdited = submittedProfile !== null && !sameRequest(profile, submittedProfile)
  const isStale = Boolean(mealPlan) && (profileEdited || requestEdited)

  // A 422 maps back to each field it names until that field is edited.
  const rejectedFields = profileErrorsFrom422(errorDetail)
  const serverErrors = errorsForUnchangedFields(rejectedFields, profile, submittedProfile)
  const fieldErrors = { ...serverErrors, ...profileErrors }
  const rejectedRequest = requestErrorsFrom422(errorDetail)
  const requestFieldErrors = { ...requestErrors }
  for (const [key, message] of Object.entries(rejectedRequest || {})) {
    if (!requestFieldErrors[key] && requestValues[key].trim() === submitted?.[key]) {
      requestFieldErrors[key] = message
    }
  }
  let errorMessage = error
  if (Array.isArray(errorDetail)) {
    errorMessage =
      rejectedFields || rejectedRequest
        ? 'The service could not use some of your details. Check the highlighted fields.'
        : `The service rejected this request: ${describeRejection(errorDetail)}`
  }

  const canSubmit = useMemo(
    () => craving.trim() && requestIsValid && profileIsValid && !isLoading,
    [craving, requestIsValid, profileIsValid, isLoading],
  )

  const submitPlan = async () => {
    clearMealPlan()
    setSubmitted({
      craving: craving.trim(),
      location: location.trim(),
      userId: userId.trim(),
      profile,
    })
    await requestMealPlan({
      user_id: userId.trim(),
      craving: craving.trim(),
      location: location.trim(),
      ...profileToRequest(profile),
    })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!canSubmit) return
    await submitPlan()
  }

  return (
    <div className="flex flex-col gap-6">
      <ProfileForm errors={fieldErrors} onChange={setProfile} profile={profile} />

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <aside className="rounded-2xl border border-gray-100 bg-white p-6 shadow-md lg:sticky lg:top-6 lg:self-start">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-accent-text">
                Step 2 · Craving
              </p>
              <h2 className="mt-1 text-lg font-semibold text-gray-900">Plan Request</h2>
              <p className="mt-1 text-sm leading-6 text-gray-500">
                Describe a dish or a feeling. We match it against our menu and tell you plainly
                if nothing is close.
              </p>
            </div>
            <div className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
              Live
            </div>
          </div>

          <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            <InputField
              error={requestFieldErrors.craving}
              label="Craving Input"
              placeholder="High-protein burger"
              value={craving}
              onChange={(event) => setCraving(event.target.value)}
            />

            <CravingSuggestions onPick={setCraving} />

            <InputField
              error={requestFieldErrors.location}
              helperText="Where you shop, for the shopping list."
              label="Location"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
            />

            <InputField
              error={requestFieldErrors.userId}
              helperText="Used to retrieve profile preferences and dietary context."
              label="User ID"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
            />

            <SubmitButton
              disabled={!canSubmit}
              idleLabel="Generate Meal Plan"
              isLoading={isLoading}
              loadingLabel="Orchestrating Agents..."
            />
            {!profileIsValid && (
              <p className="text-sm text-accent-text">Fix your details above to plan a meal.</p>
            )}
          </form>

          <ul className="mt-6 space-y-3 border-t border-line pt-5 text-sm">
            <li>
              <p className="font-semibold text-ink">Matched to a real menu</p>
              <p className="text-muted">Every meal comes from a tested recipe, never made up on the spot.</p>
            </li>
            <li>
              <p className="font-semibold text-ink">Honest when it misses</p>
              <p className="text-muted">No close match? You get a standard meal and a note saying so.</p>
            </li>
            <li>
              <p className="font-semibold text-ink">Shopping list included</p>
              <p className="text-muted">Ingredients mapped to store aisles, with estimated prices.</p>
            </li>
          </ul>

          {error && <div className="mt-5"><ErrorBanner>{errorMessage}</ErrorBanner></div>}
        </aside>

        <div className="grid content-start gap-6">
          {isStale && (
            <div
              className="flex flex-col gap-3 rounded-[14px] border border-accent-text bg-ground p-4 text-ink sm:flex-row sm:items-center sm:justify-between"
              role="status"
            >
              <p className="text-sm">
                <span className="font-semibold">Made for your previous details.</span> Your
                details or craving have changed since this plan was made.
              </p>
              <button
                className="min-h-[44px] rounded-xl bg-accent px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                disabled={!canSubmit}
                onClick={submitPlan}
                type="button"
              >
                Plan again with these details
              </button>
            </div>
          )}

          {!mealPlan && (
            <EmptyState
              idleBody="Enter a craving to generate your personalized meal plan, nutrition macros, and grocery list."
              idleTitle="Enter a craving to generate your plan"
              isLoading={isLoading}
              loadingBody="The meal, nutrition, and grocery agents are coordinating a personalized result."
              loadingTitle="Orchestrating your agents"
            />
          )}

          {isInfeasible && (
            <EmptyState
              idleBody={mealPlan.infeasible_reason}
              idleTitle="No meal fits these constraints"
              isLoading={false}
            />
          )}

          {mealPlan && !isInfeasible && (
            <MealPlanResult
              craving={submitted?.craving ?? ''}
              ingredients={ingredients}
              location={submitted?.location ?? ''}
              macroBalance={mealPlan.macro_balance}
              mealDefinition={mealDefinition}
              nutrition={nutrition}
              planStatus={mealPlan.plan_status}
              reconciliation={mealPlan.reconciliation}
              shopping={shopping}
              shoppingItems={shoppingItems}
              warnings={mealPlan.meal_plan?.metadata?.warnings || []}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default MealPlanTab
