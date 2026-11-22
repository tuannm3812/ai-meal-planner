import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import { pageShell, secondaryButton } from '../components/ui/styles'
import { HOSTED_FEEDBACK_MESSAGE } from '../features/plan/feedback'
import { findPlan } from '../features/meals/meals'
import { useMealLists } from '../features/meals/useMealLists'
import PlanDetail from '../features/plan/PlanDetail'

// A saved or past plan, read back from this device's history (spec §4.4). It
// shows the stored response as it was; nothing is planned again.
function StoredPlanPage() {
  const { requestId } = useParams()
  const planner = usePlannerContext()
  const navigate = useNavigate()
  const lists = useMealLists(planner.userId, { enabled: planner.hasProfile })
  const [ticked, setTicked] = useState(() => new Set())
  const plan = lists.status === 'ready' ? findPlan(lists.raw, requestId) : null
  const record = planner.feedback[requestId]
  const savedOnServer = lists.saved.some((meal) => meal.requestId === requestId)

  useEffect(() => {
    if (plan) document.getElementById('plan-heading')?.focus()
  }, [plan])

  const toggle = (id) =>
    setTicked((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })

  if (lists.status !== 'ready') {
    return (
      <main className={`${pageShell} py-10`}>
        {lists.status === 'hosted' ? (
          <p className="rounded-2xl bg-surface p-4 text-muted">{HOSTED_FEEDBACK_MESSAGE}</p>
        ) : lists.status === 'error' ? (
          <p className="rounded-2xl bg-surface p-4 text-accent-text" role="alert">
            {lists.error}
          </p>
        ) : (
          <p className="text-muted">Loading…</p>
        )}
      </main>
    )
  }

  if (!plan) {
    return (
      <main className={`${pageShell} py-10`}>
        <h1 className="font-display text-3xl font-extrabold">This plan is no longer in your history</h1>
        <p className="mt-2 text-muted">History lives on the API you are connected to, and it can be reset.</p>
        <Link className={`${secondaryButton} mt-5`} to="/meals">
          Back to My meals
        </Link>
      </main>
    )
  }

  if (plan.plan_status === 'infeasible') {
    return (
      <main className={`${pageShell} py-10`}>
        <h1 className="font-display text-3xl font-extrabold">No meal fits these constraints</h1>
        <p className="mt-2 text-muted">{plan.infeasible_reason || 'The service found no meal for this request.'}</p>
      </main>
    )
  }

  const planRunnerUp = async (name) => {
    navigate('/plan')
    await planner.submitPlan(name)
  }

  return (
    <main>
      <PlanDetail
        craving={plan.request?.craving ?? ''}
        feedback={{
          userId: planner.userId,
          off: planner.feedbackOff,
          saved: savedOnServer || Boolean(record?.saved),
          rating: record?.rating ?? null,
          onSaved: () => planner.markFeedback(requestId, { saved: true }),
          onRated: (rating) => planner.markFeedback(requestId, { rating }),
          onHosted: () => planner.setFeedbackOff(true),
        }}
        location={plan.request?.location ?? ''}
        onPlanRunnerUp={planRunnerUp}
        onToggle={toggle}
        onTryAnother={() => navigate('/')}
        plan={plan}
        runnerUpDisabled={planner.isLoading || planner.retryPause.active}
        ticked={ticked}
      />
    </main>
  )
}

export default StoredPlanPage
