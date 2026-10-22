import { useEffect, useMemo, useRef, useState } from 'react'

import { generateMealPlan } from '../../api/mealPlanner'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import EmptyState from '../../components/ui/EmptyState'
import InputField from '../../components/ui/InputField'
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
import StepIndicator from './StepIndicator'

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

const primaryButton =
  'min-h-[52px] rounded-xl bg-accent px-7 font-semibold text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-600'
const secondaryButton =
  'min-h-[44px] rounded-xl border border-ink px-4 text-sm font-semibold text-ink hover:bg-surface focus:outline-none focus-visible:ring-2 focus-visible:ring-ink'

// Each step's heading takes focus when the step opens, so keyboard and
// screen-reader users land at the top of what changed.
const HEADINGS = { profile: 'profile-heading', craving: 'craving-heading', plan: 'plan-step-heading' }

// The guided flow of docs/8_design.md §3: you, then craving, then the plan.
// Every step stays mounted in state here, so going back keeps what was
// entered and the plan stays until something it depends on changes.
//
// `profile` and `userId` come from App. Rendered on its own (as in the flow's
// tests), it holds its own profile and `initialStep` can open a later step.
function MealFlow({
  profile: sharedProfile,
  onProfileChange,
  userId = 'web-local-user',
  initialStep = 'profile',
}) {
  const [step, setStep] = useState(initialStep)
  const [craving, setCravingValue] = useState('')
  const [location, setLocationValue] = useState('Earlwood, NSW')
  // Set when an edit dropped a plan that was still being made.
  const [droppedInFlight, setDroppedInFlight] = useState(false)
  const opened = useRef(false)
  // Shopping-list ticks, for one plan: kept across steps, cleared when a new
  // plan arrives (a different key).
  const [ticks, setTicks] = useState({ plan: null, ids: new Set() })
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

  useEffect(() => {
    // Not on first render: the page opens at the top, as any page does.
    if (!opened.current) {
      opened.current = true
      return
    }
    document.getElementById(HEADINGS[step])?.focus()
  }, [step])

  // G3: "infeasible" is a successful response with null meal sections.
  const isInfeasible = mealPlan?.plan_status === 'infeasible'

  const planKey = mealPlan ? (mealPlan.request_id ?? JSON.stringify(mealPlan.shopping_list)) : null
  const ticked = ticks.plan === planKey ? ticks.ids : new Set()
  const toggleTick = (id) => {
    const ids = new Set(ticked)
    if (ids.has(id)) ids.delete(id)
    else ids.add(id)
    setTicks({ plan: planKey, ids })
  }

  const profileErrors = useMemo(() => validateProfile(profile), [profile])
  const profileIsValid = Object.keys(profileErrors).length === 0
  const requestValues = { craving, location, userId }
  const requestErrors = validateRequest(requestValues)
  const requestIsValid = Object.keys(requestErrors).length === 0
  const requestEdited =
    submitted !== null &&
    (craving.trim() !== submitted.craving || location.trim() !== submitted.location)
  const profileEdited = submittedProfile !== null && !sameRequest(profile, submittedProfile)
  const isStale = Boolean(mealPlan) && (profileEdited || requestEdited)

  // A 422 maps back to each field it names until that field is edited. The
  // user ID is generated, not typed, so a 422 on it has no field to mark.
  const rejectedFields = profileErrorsFrom422(errorDetail)
  const serverErrors = errorsForUnchangedFields(rejectedFields, profile, submittedProfile)
  const fieldErrors = { ...serverErrors, ...profileErrors }
  const rejectedOnScreen = { ...requestErrorsFrom422(errorDetail) }
  delete rejectedOnScreen.userId
  const rejectedRequest = Object.keys(rejectedOnScreen).length ? rejectedOnScreen : null
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
        ? 'The service could not use some of your details. Go back to the highlighted fields.'
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
  const setProfile = (next) => {
    dropIfInFlight(!sameRequest(next, submitted?.profile ?? next))
    storeProfile(next)
  }

  const submitPlan = async () => {
    if (retryPause.active) return
    clearMealPlan()
    setDroppedInFlight(false)
    setSubmitted({ craving: craving.trim(), location: location.trim(), profile })
    await requestMealPlan({
      user_id: userId,
      craving: craving.trim(),
      location: location.trim(),
      ...profileToRequest(profile),
    })
  }

  const handleCravingSubmit = async (event) => {
    event.preventDefault()
    if (!canSubmit) return
    setStep('plan')
    await submitPlan()
  }

  const handleProfileNext = (event) => {
    event.preventDefault()
    if (profileIsValid) setStep('craving')
  }

  const reachable = {
    profile: true,
    craving: profileIsValid,
    plan: submitted !== null,
  }

  return (
    <div className="flex flex-col gap-6">
      <StepIndicator current={step} onGo={setStep} reachable={reachable} />

      {step === 'profile' && (
        <form className="flex flex-col gap-6" noValidate onSubmit={handleProfileNext}>
          <ProfileForm errors={fieldErrors} onChange={setProfile} profile={profile} />
          <div className="flex flex-wrap items-center gap-4">
            <button className={primaryButton} disabled={!profileIsValid} type="submit">
              Next: what are you craving?
            </button>
            <span className="text-sm text-muted">
              {profileIsValid
                ? 'You can change these at any time.'
                : 'Fix the highlighted details to continue.'}
            </span>
          </div>
        </form>
      )}

      {step === 'craving' && (
        <section
          aria-labelledby="craving-heading"
          className="rounded-[20px] border border-line bg-surface p-6 sm:p-8"
        >
          <p className="text-sm font-semibold uppercase tracking-wider text-accent-text">
            Step 2 · Craving
          </p>
          <h1
            className="mt-2 font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl"
            id="craving-heading"
            tabIndex={-1}
          >
            What are you in the mood for?
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-muted">
            Describe a dish or a feeling. We match it against our menu and tell you plainly if
            nothing is close.
          </p>

          <form className="mt-8 flex max-w-2xl flex-col gap-6" onSubmit={handleCravingSubmit}>
            <InputField
              error={requestFieldErrors.craving}
              label="Your craving"
              placeholder="High-protein burger"
              value={craving}
              onChange={(event) => setCraving(event.target.value)}
            />

            <CravingSuggestions onPick={setCraving} />

            <InputField
              error={requestFieldErrors.location}
              helperText="Used to pick a store for the shopping list."
              label="Where you shop"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
            />

            <div className="flex flex-wrap items-center gap-3">
              <button className={primaryButton} disabled={!canSubmit} type="submit">
                Plan my meal
              </button>
              <button className={secondaryButton} onClick={() => setStep('profile')} type="button">
                Back: your details
              </button>
            </div>
            {retryPause.active && (
              <p className="text-sm text-accent-text">
                The server asked for a pause. You can plan again in about {retryPause.seconds}{' '}
                seconds.
              </p>
            )}
          </form>

          <ul className="mt-8 grid gap-4 border-t border-line pt-6 text-sm sm:grid-cols-3">
            <li>
              <p className="font-semibold text-ink">Matched to a real menu</p>
              <p className="text-muted">
                Every meal comes from a tested recipe, never made up on the spot.
              </p>
            </li>
            <li>
              <p className="font-semibold text-ink">Honest when it misses</p>
              <p className="text-muted">
                No close match? You get a standard meal and a note saying so.
              </p>
            </li>
            <li>
              <p className="font-semibold text-ink">Shopping list included</p>
              <p className="text-muted">
                Ingredients mapped to store aisles, with estimated prices.
              </p>
            </li>
          </ul>
        </section>
      )}

      {step === 'plan' && (
        <div aria-live="polite" className="grid min-w-0 grid-cols-[minmax(0,1fr)] gap-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h1
              className="font-display text-2xl font-bold text-ink"
              id="plan-step-heading"
              tabIndex={-1}
            >
              Your plan
            </h1>
            <div className="flex flex-wrap gap-3">
              <button className={secondaryButton} onClick={() => setStep('profile')} type="button">
                Change your details
              </button>
              <button className={secondaryButton} onClick={() => setStep('craving')} type="button">
                Try another craving
              </button>
            </div>
          </div>

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
              className="rounded-[14px] border border-accent-text bg-surface p-4 text-sm text-ink"
              role="status"
            >
              <span className="font-semibold">Plan set aside.</span> Your details or craving
              changed while it was being made, so it was not shown. Plan again when you are
              ready.
            </div>
          )}

          {isStale && (
            <div
              className="flex flex-col gap-3 rounded-[14px] border border-accent-text bg-surface p-4 text-ink sm:flex-row sm:items-center sm:justify-between"
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

          {!mealPlan && isLoading && (
            // Indeterminate: one POST reports no stages, so none are shown.
            <EmptyState
              idleBody=""
              idleTitle=""
              isLoading
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
            </section>
          )}

          {mealPlan && !isInfeasible && (
            <>
              <PlanView craving={submitted?.craving ?? ''} plan={mealPlan} />
              <ShoppingList
                location={submitted?.location ?? ''}
                onToggle={toggleTick}
                shopping={mealPlan.shopping_list}
                ticked={ticked}
              />
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default MealFlow
