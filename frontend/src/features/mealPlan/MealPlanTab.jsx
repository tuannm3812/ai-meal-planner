import { useMemo, useRef, useState } from 'react'

import { generateMealPlan } from '../../api/mealPlanner'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import EmptyState from '../../components/ui/EmptyState'
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
import FailurePanel from '../plan/FailurePanel'
import PlanView from '../plan/PlanView'
import ShoppingList from '../plan/ShoppingList'
import { useRetryPause } from '../plan/useRetryPause'

// A 422 that names no field on screen still says what the service rejected,
// rather than the "is the backend running" sentence.
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
  const [craving, setCravingValue] = useState('')
  const [userId, setUserIdValue] = useState('user_123')
  const [location, setLocationValue] = useState('Earlwood, NSW')
  // Set when an edit dropped a plan that was still being made.
  const [droppedInFlight, setDroppedInFlight] = useState(false)
  const cravingRef = useRef(null)
  // The profile is React state only: never the URL, never browser storage.
  const [ownProfile, setOwnProfile] = useState(DEFAULT_PROFILE)
  const profile = sharedProfile ?? ownProfile
  const storeProfile = onProfileChange ?? setOwnProfile
  // What the last request was sent with. The result names this craving and
  // location, not the live inputs, and a plan made for anything else is
  // marked stale rather than shown as current.
  const [submitted, setSubmitted] = useState(null)
  const submittedProfile = submitted?.profile ?? null
  const {
    data: mealPlan,
    error,
    errorDetail,
    failure,
    isLoading,
    run: requestMealPlan,
    reset: clearMealPlan,
  } = useAsyncRequest(
    generateMealPlan,
    'Could not generate a meal plan. Check that the FastAPI backend is running on port 8000.',
  )

  // G3: "infeasible" is a successful response with null meal sections.
  const isInfeasible = mealPlan?.plan_status === 'infeasible'

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
  // Only a 422's list needs wording here; FailurePanel words every other failure.
  let errorMessage = null
  if (Array.isArray(errorDetail)) {
    errorMessage =
      rejectedFields || rejectedRequest
        ? 'The service could not use some of your details. Check the highlighted fields.'
        : `The service rejected this request: ${describeRejection(errorDetail)}`
  }

  // After a 429 nothing is sent until the pause passes, by any route.
  const retryPause = useRetryPause(failure)

  const canSubmit = useMemo(
    () =>
      craving.trim() && requestIsValid && profileIsValid && !isLoading && !retryPause.active,
    [craving, requestIsValid, profileIsValid, isLoading, retryPause.active],
  )

  // The in-flight guard (docs/8_design.md §3.3): an edit that changes what
  // the pending request asked for drops its answer, rather than showing a plan
  // for inputs the person has already changed. A plan that completed before
  // the edit stays, marked stale.
  const dropIfInFlight = (changed) => {
    if (isLoading && submitted && changed) {
      clearMealPlan()
      setDroppedInFlight(true)
    }
  }
  const setCraving = (value) => {
    dropIfInFlight(value.trim() !== submitted?.craving)
    setCravingValue(value)
  }
  const setLocation = (value) => {
    dropIfInFlight(value.trim() !== submitted?.location)
    setLocationValue(value)
  }
  const setUserId = (value) => {
    dropIfInFlight(value.trim() !== submitted?.userId)
    setUserIdValue(value)
  }
  const setProfile = (next) => {
    dropIfInFlight(!sameRequest(next, submitted?.profile ?? next))
    storeProfile(next)
  }

  // Back to an earlier step, keeping everything entered there.
  const focusCraving = () => cravingRef.current?.focus()
  const focusProfile = () => document.getElementById('profile-heading')?.focus()

  const submitPlan = async () => {
    if (retryPause.active) return
    clearMealPlan()
    setDroppedInFlight(false)
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

      <div className="grid grid-cols-[minmax(0,1fr)] gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
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
              ref={cravingRef}
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
              loadingLabel="Planning your meal…"
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

        </aside>

        <div aria-live="polite" className="grid min-w-0 grid-cols-[minmax(0,1fr)] content-start gap-6">
          {error && (
            <FailurePanel
              canRetry={canSubmit}
              failure={failure}
              message={errorMessage}
              onRetry={submitPlan}
              pause={retryPause}
            />
          )}

          {droppedInFlight && !isLoading && !mealPlan && (
            <div
              className="rounded-[14px] border border-accent-text bg-ground p-4 text-sm text-ink"
              role="status"
            >
              <span className="font-semibold">Plan set aside.</span> Your details or craving
              changed while it was being made, so it was not shown. Plan again when you are
              ready.
            </div>
          )}

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

          {!mealPlan && (isLoading || !error) && (
            // Indeterminate: one POST reports no stages, so none are shown.
            <EmptyState
              idleBody="Enter a craving to plan a meal sized to you, with its nutrition and a shopping list."
              idleTitle="Enter a craving to plan your meal"
              isLoading={isLoading}
              loadingBody="This can take a few seconds."
              loadingTitle="Planning your meal…"
            />
          )}

          {isInfeasible && (
            <section className="rounded-[20px] border border-line bg-surface p-6">
              <h2 className="font-display text-2xl font-bold text-ink">
                No meal fits these constraints
              </h2>
              <p className="mt-2 text-muted">
                {mealPlan.infeasible_reason || 'The service found no meal for this request.'}
              </p>
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  className="min-h-[44px] rounded-xl border border-ink px-4 text-sm font-semibold text-ink"
                  onClick={focusProfile}
                  type="button"
                >
                  Change your details
                </button>
                <button
                  className="min-h-[44px] rounded-xl border border-ink px-4 text-sm font-semibold text-ink"
                  onClick={focusCraving}
                  type="button"
                >
                  Try another craving
                </button>
              </div>
            </section>
          )}

          {mealPlan && !isInfeasible && (
            <>
              <PlanView
                craving={submitted?.craving ?? ''}
                onEditCraving={focusCraving}
                plan={mealPlan}
              />
              <ShoppingList
                key={mealPlan.request_id ?? JSON.stringify(mealPlan.shopping_list)}
                location={submitted?.location ?? ''}
                shopping={mealPlan.shopping_list}
              />
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default MealPlanTab
