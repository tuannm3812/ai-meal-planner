import { ArrowLeft, ArrowRight, Flame, Info, PieChart } from 'lucide-react'
import { Link } from 'react-router-dom'

import BlobShape from '../../components/illustrations/BlobShape'
import DishIllustration from '../../components/illustrations/DishIllustration'
import { card, ghostButton, pageShell, sectionHeading } from '../../components/ui/styles'
import CalorieRing from './charts/CalorieRing'
import CalorieSources from './charts/CalorieSources'
import MacroDonut from './charts/MacroDonut'
import RangeBars from './charts/RangeBars'
import { HOSTED_FEEDBACK_MESSAGE } from './feedback'
import {
  balanceOutcome,
  calories,
  estimatedCount,
  howItWasMade,
  ingredients,
  matchBadge,
  servedSplit,
} from './plan'
import RatingCard from './RatingCard'
import { runnersUp } from './runnersUp'
import SaveButton from './SaveButton'
import ShoppingList from './ShoppingList'

const TONES = {
  good: 'bg-success-bg text-success-fg',
  warn: 'bg-estimate-bg text-estimate-fg',
  info: 'bg-white/10 text-white',
}

function Badge({ tone = 'info', children }) {
  return (
    <span className={`rounded-full px-3.5 py-1.5 text-sm font-semibold ${TONES[tone]}`}>
      {children}
    </span>
  )
}

// The plan page body (spec §4.3). It renders one response, top to bottom, and
// keeps plan_status, the balance outcome, the final nutrition and the
// warnings apart, as docs/8_design.md §3.3 asks. `feedback` is null where
// saving and rating don't apply.
function PlanDetail({
  plan,
  craving,
  location,
  ticked,
  onToggle,
  onTryAnother,
  onPlanRunnerUp,
  runnerUpDisabled = false,
  feedback,
}) {
  const match = matchBadge(plan)
  const outcome = balanceOutcome(plan)
  const estimated = estimatedCount(plan)
  const energy = calories(plan)
  const split = servedSplit(plan?.nutrition)
  const items = ingredients(plan)
  const notes = howItWasMade(plan)
  const others = onPlanRunnerUp ? runnersUp(plan) : []
  const mealName = plan?.meal_plan?.meal_definition?.structured_meal_name || 'Untitled meal'

  return (
    <>
      <section aria-labelledby="plan-heading" className="bg-ink text-white">
        <div className={`${pageShell} relative overflow-hidden pb-8 pt-5`}>
          <div className="relative flex flex-wrap items-center gap-8">
            <div className="flex min-w-0 flex-[3_1_480px] flex-col gap-3.5">
              <Link
                className="inline-flex min-h-[44px] w-fit items-center gap-1.5 rounded-xl text-sm text-[#C9D3CC] hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-viridis-5 print:hidden"
                to="/"
              >
                <ArrowLeft aria-hidden="true" size={18} />
                Home
              </Link>
              {craving && <p className="text-[15px] text-[#C9D3CC]">For your craving &ldquo;{craving}&rdquo;</p>}
              <h1
                className="font-display text-4xl font-extrabold leading-none tracking-tight sm:text-[56px]"
                id="plan-heading"
                tabIndex={-1}
              >
                {mealName}
              </h1>
              <div className="flex flex-wrap gap-2">
                {match && <Badge tone={match.tone}>{match.label}</Badge>}
                {outcome && <Badge tone={outcome.tone}>{outcome.label}</Badge>}
                {estimated && <Badge tone="warn">Some nutrition estimated</Badge>}
              </div>
              <div className="mt-2 flex flex-wrap items-start gap-3 print:hidden">
                {feedback && !feedback.off && (
                  <SaveButton
                    onHosted={feedback.onHosted}
                    onSaved={feedback.onSaved}
                    plan={plan}
                    saved={feedback.saved}
                    userId={feedback.userId}
                  />
                )}
                {onTryAnother && (
                  <button className={ghostButton} onClick={onTryAnother} type="button">
                    Try another craving
                  </button>
                )}
              </div>
            </div>
            <div className="relative hidden w-[300px] shrink-0 md:block" aria-hidden="true">
              <BlobShape className="absolute -left-6 -top-10 w-[340px]" />
              <DishIllustration className="relative w-[300px]" mealName={mealName} />
            </div>
          </div>

          {plan?.plan_status === 'fallback' && (
            <p className="relative mt-6 rounded-2xl bg-estimate-bg px-4 py-3 text-[15px] text-estimate-fg">
              Nothing on the menu is a close match for &ldquo;{craving}&rdquo;, so this is a
              standard meal instead.
            </p>
          )}

          {estimated && (
            <p className="relative mt-6 flex items-start gap-3 rounded-2xl bg-estimate-bg px-4 py-3 text-[15px] text-estimate-fg">
              <Info aria-hidden="true" className="mt-0.5 shrink-0" size={22} />
              <span>
                {estimated.estimated} of {estimated.of} ingredients use estimated nutrition from
                local tables, so these numbers are approximate.
                {outcome &&
                  ' “On target” is measured against those same tables, so it is not an independent check.'}
              </span>
            </p>
          )}
          {feedback?.off && (
            <p className="relative mt-4 text-sm text-[#C9D3CC]" role="status">
              {HOSTED_FEEDBACK_MESSAGE}
            </p>
          )}
        </div>
      </section>

      <div className={`${pageShell} flex flex-wrap items-start gap-6 py-6`}>
        <div className="flex min-w-0 flex-[3_1_560px] flex-col gap-6">
          {(energy || split || outcome) && (
            <section aria-labelledby="nutrition-heading" className={card}>
              <h2 className={sectionHeading} id="nutrition-heading">
                <Flame aria-hidden="true" className="text-carbs" size={32} strokeWidth={1.8} />
                Nutrition
              </h2>
              {energy && (
                <div className="mt-5 flex flex-wrap items-center gap-8">
                  <CalorieRing target={energy.target} total={energy.total} />
                  {split && <MacroDonut grams={energy.grams} split={split} />}
                </div>
              )}

              <section aria-labelledby="balance-heading" className="mt-7">
                <h3 className="text-[17px] font-semibold text-ink" id="balance-heading">
                  Balance
                </h3>
                {outcome && <p className="mt-1 text-sm text-muted">{outcome.body}</p>}
                {plan?.reconciliation?.rescaled && outcome && (
                  <p className="mt-1 text-sm text-muted">
                    All portions were then scaled toward the meal&rsquo;s calorie target.
                  </p>
                )}
                {split ? (
                  <>
                    <div className="mt-4">
                      <RangeBars split={split} />
                    </div>
                    {outcome && (
                      <p className="mt-3 text-sm text-muted">
                        The green band is the recommended range. The verdict above is the
                        service&rsquo;s, not read from these bars.
                      </p>
                    )}
                  </>
                ) : (
                  <p className="mt-3 text-sm text-muted">This response has no nutrition to split.</p>
                )}
              </section>
            </section>
          )}

          {items.length > 0 && (
            <section aria-labelledby="sources-heading" className={card}>
              <h2 className={sectionHeading} id="sources-heading">
                <PieChart aria-hidden="true" className="text-protein" size={32} strokeWidth={1.8} />
                Where the calories come from
              </h2>
              <p className="mb-4 mt-1 text-sm text-muted">
                Each ingredient&rsquo;s share of this meal, with its served portion.
              </p>
              <CalorieSources items={items} />
            </section>
          )}

          {others.length > 0 && (
            <section aria-labelledby="also-heading" className="rounded-3xl bg-tint p-6 print:hidden">
              <h2 className="font-display text-[22px] font-extrabold text-ink" id="also-heading">
                Also close to your craving
              </h2>
              <ul className="mt-3 flex flex-wrap gap-2.5">
                {others.map((meal) => (
                  <li key={meal.id}>
                    <button
                      className="inline-flex min-h-[48px] items-center gap-2 rounded-2xl bg-surface px-4 font-semibold text-ink hover:ring-2 hover:ring-carbs focus:outline-none focus-visible:ring-2 focus-visible:ring-ink disabled:cursor-not-allowed disabled:opacity-60"
                      disabled={runnerUpDisabled}
                      onClick={() => onPlanRunnerUp(meal.name)}
                      type="button"
                    >
                      {meal.name}
                      <ArrowRight aria-hidden="true" size={18} />
                    </button>
                  </li>
                ))}
              </ul>
              <p className="mt-2.5 text-sm text-success-fg">
                Choosing one plans that meal for you, sized the same way.
              </p>
            </section>
          )}

          {notes.length > 0 && (
            <details className={`${card} print:hidden`}>
              <summary className="min-h-[24px] cursor-pointer font-semibold text-ink">
                How this plan was made
              </summary>
              <ul className="mt-3 list-disc space-y-1.5 pl-5 text-sm text-muted">
                {notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </details>
          )}
        </div>

        <aside className="flex min-w-0 flex-[2_1_340px] flex-col gap-6" aria-label="Shopping and rating">
          <ShoppingList
            location={location}
            mealName={mealName}
            onToggle={onToggle}
            shopping={plan.shopping_list}
            ticked={ticked}
          />
          {feedback && !feedback.off && (
            <RatingCard
              onHosted={feedback.onHosted}
              onRated={feedback.onRated}
              plan={plan}
              sentRating={feedback.rating ?? null}
              userId={feedback.userId}
            />
          )}
        </aside>
      </div>
    </>
  )
}

export default PlanDetail
