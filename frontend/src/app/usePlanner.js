import { useMemo, useState } from 'react'

import { generateMealPlan } from '../api/mealPlanner'
import { useAsyncRequest } from '../hooks/useAsyncRequest'
import { requestErrorsFrom422, validateRequest } from '../features/craving/craving'
import {
  DEFAULT_PROFILE,
  errorsForUnchangedFields,
  profileErrorsFrom422,
  profileToRequest,
  sameRequest,
  validateProfile,
} from '../features/profile/profile'
import { useRetryPause } from '../features/plan/useRetryPause'
import { clearStored, loadStored, saveStored } from './storage'

export const DEFAULT_LOCATION = 'Earlwood, NSW'

// An opaque ID for this device (docs/8_design.md §3.1). It is in history
// URLs, which access logs record, so it says nothing about anyone.
export function newUserId() {
  return `web-${globalThis.crypto.randomUUID()}`
}

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

function initialState() {
  const stored = loadStored()
  return {
    userId: stored?.userId ?? newUserId(),
    profile: stored?.profile ? { ...DEFAULT_PROFILE, ...stored.profile } : DEFAULT_PROFILE,
    location: stored?.location ?? DEFAULT_LOCATION,
    // A first visit asks for the profile before anything else (spec §4.1).
    hasProfile: Boolean(stored?.profile),
  }
}

// The meal planner's state, shared by every page through PlannerContext.
// The request logic is the old MealFlow's, unchanged: the stale mark, the
// in-flight guard, 422 mapping and the 429 pause all behave as before.
export function usePlanner() {
  const [initial] = useState(initialState)
  const [userId, setUserId] = useState(initial.userId)
  const [profile, setProfileValue] = useState(initial.profile)
  const [location, setLocationValue] = useState(initial.location)
  const [hasProfile, setHasProfile] = useState(initial.hasProfile)
  const [canRemember, setCanRemember] = useState(true)
  const [craving, setCravingValue] = useState('')
  // Set when an edit dropped a plan that was still being made.
  const [droppedInFlight, setDroppedInFlight] = useState(false)
  // Shopping-list ticks, for one plan: kept across pages, cleared when a new
  // plan arrives (a different key). Never sent or stored.
  const [ticks, setTicks] = useState({ plan: null, ids: new Set() })
  // What this visit saved or rated, by request ID, and whether the server
  // refused feedback (a hosted deployment answers 501).
  const [feedback, setFeedback] = useState({})
  const [feedbackOff, setFeedbackOff] = useState(false)
  // What the last request was sent with. The plan names this craving and
  // location, not the live inputs, and a plan made for anything else is
  // marked stale rather than shown as current.
  const [submitted, setSubmitted] = useState(null)
  const submittedProfile = submitted?.profile ?? null
  const {
    data: plan,
    error,
    errorDetail,
    failure,
    isLoading,
    run: requestMealPlan,
    reset: clearPlan,
  } = useAsyncRequest(
    generateMealPlan,
    'Could not generate a meal plan. Check your connection and try again.',
  )

  // Remember on this device once the person has given their details, on
  // every change after that.
  const persist = (changes, remember = hasProfile) => {
    if (!remember) return
    setCanRemember(saveStored({ userId, profile, location, ...changes }))
  }

  const planKey = plan ? (plan.request_id ?? JSON.stringify(plan.shopping_list)) : null
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
  const isStale = Boolean(plan) && (profileEdited || requestEdited)

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
        ? 'The service could not use some of your details. Fix the highlighted fields.'
        : `The service rejected this request: ${describeRejection(errorDetail)}`
  }

  // After a 429 nothing is sent until the pause passes, by any route.
  const retryPause = useRetryPause(failure)

  const canSubmit = Boolean(
    craving.trim() && requestIsValid && profileIsValid && !isLoading && !retryPause.active,
  )

  // The in-flight guard (docs/8_design.md §3.3): an edit that changes what
  // the pending request asked for drops its answer, rather than showing a plan
  // for inputs the person has already changed. A plan that completed before
  // the edit stays, marked stale.
  const dropIfInFlight = (changed) => {
    if (isLoading && submitted && changed) {
      clearPlan()
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
    persist({ location: value })
  }
  const setProfile = (next) => {
    dropIfInFlight(!sameRequest(next, submitted?.profile ?? next))
    setProfileValue(next)
    persist({ profile: next })
  }

  // `cravingOverride` plans a runner-up: the same profile and location with
  // that meal's name as the craving.
  const submitPlan = async (cravingOverride) => {
    if (retryPause.active) return
    const wanted = (typeof cravingOverride === 'string' ? cravingOverride : craving).trim()
    if (typeof cravingOverride === 'string') setCravingValue(cravingOverride)
    clearPlan()
    setDroppedInFlight(false)
    setSubmitted({ craving: wanted, location: location.trim(), profile })
    await requestMealPlan({
      user_id: userId,
      craving: wanted,
      location: location.trim(),
      ...profileToRequest(profile),
    })
  }

  const markFeedback = (requestId, values) =>
    setFeedback((current) => ({ ...current, [requestId]: { ...current[requestId], ...values } }))

  // "Forget me on this device": a new ID, the default details, no plan, and
  // the first-visit screen again. Server history is not touched.
  const forget = () => {
    clearStored()
    clearPlan()
    setSubmitted(null)
    setDroppedInFlight(false)
    setTicks({ plan: null, ids: new Set() })
    setFeedback({})
    setUserId(newUserId())
    setProfileValue(DEFAULT_PROFILE)
    setLocationValue(DEFAULT_LOCATION)
    setCravingValue('')
    setHasProfile(false)
  }

  // A signed-in account's saved details replace this device's (DEC-43).
  const adoptAccount = (accountProfile, accountLocation) => {
    const next = { ...DEFAULT_PROFILE, ...accountProfile }
    const nextLocation = accountLocation || location
    setProfileValue(next)
    setLocationValue(nextLocation)
    setHasProfile(true)
    persist({ profile: next, location: nextLocation }, true)
  }

  return {
    userId,
    profile,
    setProfile,
    location,
    setLocation,
    craving,
    setCraving,
    hasProfile,
    confirmProfile: () => {
      setHasProfile(true)
      persist({}, true)
    },
    canRemember,
    forget,
    adoptAccount,
    plan,
    isLoading,
    error,
    failure,
    errorMessage,
    profileErrors,
    fieldErrors,
    requestFieldErrors,
    profileIsValid,
    canSubmit,
    isStale,
    droppedInFlight,
    submitted,
    submitPlan,
    ticked,
    toggleTick,
    retryPause,
    feedback,
    markFeedback,
    feedbackOff,
    setFeedbackOff,
  }
}
