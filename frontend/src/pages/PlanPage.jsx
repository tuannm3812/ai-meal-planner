import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import { pageShell, primaryButton, secondaryButton } from '../components/ui/styles'
import FailurePanel from '../features/plan/FailurePanel'
import PlanDetail from '../features/plan/PlanDetail'

// The plan just made (spec §4.3), with every state of docs/8_design.md §3.3:
// loading, failure, set aside, stale, infeasible, then the plan itself.
function PlanPage() {
  const planner = usePlannerContext()
  const navigate = useNavigate()
  const {
    plan,
    isLoading,
    error,
    failure,
    errorMessage,
    submitted,
    submitPlan,
    canSubmit,
    retryPause,
    droppedInFlight,
    isStale,
    feedback,
    markFeedback,
    feedbackOff,
    setFeedbackOff,
    userId,
  } = planner

  // Land keyboard and screen-reader users on what arrived.
  useEffect(() => {
    if (plan) document.getElementById('plan-heading')?.focus()
  }, [plan])

  const isInfeasible = plan?.plan_status === 'infeasible'
  const tryAnother = () => navigate('/')
  const planRunnerUp = async (name) => {
    window.scrollTo?.(0, 0)
    await submitPlan(name)
  }
  const requestId = plan?.request_id
  const record = requestId ? feedback[requestId] : null

  if (!submitted && !plan) {
    return (
      <main className={`${pageShell} py-10`}>
        <h1 className="font-display text-3xl font-extrabold">No plan yet</h1>
        <p className="mt-2 text-muted">Tell us what you crave on the home page to make one.</p>
        <Link className={`${primaryButton} mt-5`} to="/">
          Plan a meal
        </Link>
      </main>
    )
  }

  return (
    <main aria-live="polite">
      {(error || droppedInFlight || isStale || (!plan && isLoading) || isInfeasible) && (
        <div className={`${pageShell} flex flex-col gap-4 pt-6`}>
          {error && (
            <FailurePanel
              canRetry={canSubmit}
              failure={failure}
              message={errorMessage}
              onRetry={() => submitPlan()}
              pause={retryPause}
            />
          )}

          {(error || droppedInFlight) && !plan && !isLoading && (
            <div className="flex flex-wrap gap-3">
              <button className={secondaryButton} onClick={tryAnother} type="button">
                Try another craving
              </button>
              <Link className={secondaryButton} to="/profile">
                Change your details
              </Link>
            </div>
          )}

          {droppedInFlight && !isLoading && !plan && (
            <div className="rounded-2xl border border-accent-text bg-surface p-4 text-sm text-ink" role="status">
              <span className="font-semibold">Plan set aside.</span> Your details or craving
              changed while it was being made, so it was not shown. Plan again when you are
              ready.
            </div>
          )}

          {isStale && (
            <div
              className="flex flex-col gap-3 rounded-2xl border border-accent-text bg-surface p-4 text-ink sm:flex-row sm:items-center sm:justify-between"
              role="status"
            >
              <p className="text-sm">
                <span className="font-semibold">Made for your previous details.</span> Your
                details or craving have changed since this plan was made.
              </p>
              <button
                className="min-h-[44px] rounded-xl bg-accent px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-[#C9D3CC] disabled:text-ink/70"
                disabled={!canSubmit}
                onClick={() => submitPlan()}
                type="button"
              >
                Plan again with these details
              </button>
            </div>
          )}

          {!plan && isLoading && (
            // Indeterminate: one POST reports no stages, so none are shown.
            <section className="flex min-h-[360px] flex-col items-center justify-center gap-4 rounded-3xl bg-surface p-8 text-center">
              <span
                aria-hidden="true"
                className="h-12 w-12 animate-spin rounded-full border-4 border-carbs border-t-transparent"
              />
              <h1 className="font-display text-2xl font-extrabold">Planning your meal…</h1>
              <p className="text-sm text-muted">This can take a few seconds.</p>
            </section>
          )}

          {isInfeasible && (
            <section className="rounded-3xl bg-surface p-6">
              <h1 className="font-display text-2xl font-extrabold text-ink">
                No meal fits these constraints
              </h1>
              <p className="mt-2 text-muted">
                {plan.infeasible_reason || 'The service found no meal for this request.'}
              </p>
              <div className="mt-4 flex flex-wrap gap-3">
                <button className={secondaryButton} onClick={tryAnother} type="button">
                  Try another craving
                </button>
                <Link className={secondaryButton} to="/profile">
                  Change your details
                </Link>
              </div>
            </section>
          )}
        </div>
      )}

      {plan && !isInfeasible && (
        <PlanDetail
          craving={submitted?.craving ?? ''}
          feedback={
            requestId
              ? {
                  userId,
                  off: feedbackOff,
                  saved: Boolean(record?.saved),
                  rating: record?.rating ?? null,
                  onSaved: () => markFeedback(requestId, { saved: true }),
                  onRated: (rating) => markFeedback(requestId, { rating }),
                  onHosted: () => setFeedbackOff(true),
                }
              : null
          }
          location={submitted?.location ?? ''}
          onPlanRunnerUp={planRunnerUp}
          onToggle={planner.toggleTick}
          onTryAnother={tryAnother}
          plan={plan}
          runnerUpDisabled={isLoading || retryPause.active}
          ticked={planner.ticked}
        />
      )}
    </main>
  )
}

export default PlanPage
