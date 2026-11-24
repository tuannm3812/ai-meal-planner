import { useState } from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../components/icons/Icon'
import { ArrowLeft, ArrowRight, BookOpenCheck, Flame, Info, PieChart } from '../../components/icons/glyphs'
import BlobShape from '../../components/illustrations/BlobShape'
import DishIllustration from '../../components/illustrations/DishIllustration'
import PriceTag from '../../components/ui/PriceTag'
import Tabs from '../../components/ui/Tabs'
import { card, ghostButton, pageShell, sectionHeading } from '../../components/ui/styles'
import { formatCurrency } from '../../lib/format'
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
import { total } from './shopping'
import ShoppingList from './ShoppingList'

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
  const cost = total(plan?.shopping_list)
  const mealName = plan?.meal_plan?.meal_definition?.structured_meal_name || 'Untitled meal'
  // The report's tabs. A tab with nothing to show is left out, and a new plan
  // opens on Overview again.
  const tabs = [
    { id: 'overview', label: 'Overview' },
    ...(items.length ? [{ id: 'ingredients', label: 'Ingredients', count: items.length }] : []),
    ...(notes.length ? [{ id: 'made', label: 'How it was made' }] : []),
  ]
  const planKey = plan?.request_id ?? mealName
  const [chosen, setChosen] = useState({ plan: planKey, tab: 'overview' })
  const wanted = chosen.plan === planKey ? chosen.tab : 'overview'
  const tab = tabs.some((entry) => entry.id === wanted) ? wanted : 'overview'

  return (
    <>
      <section aria-labelledby="plan-heading" className="bg-cobalt text-white">
        <div className={`${pageShell} relative overflow-hidden pb-8 pt-5`}>
          <div className="relative flex flex-wrap items-center gap-8">
            <div className="flex min-w-0 flex-[3_1_480px] flex-col gap-3.5">
              <Link
                className="inline-flex min-h-[44px] w-fit items-center gap-1.5 rounded-xl text-sm text-on-ink-muted hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-peach print:hidden"
                to="/"
              >
                <Icon as={ArrowLeft} size="sm" />
                Plan a meal
              </Link>
              {craving && <p className="text-[15px] text-on-ink-muted">For your craving &ldquo;{craving}&rdquo;</p>}
              <h1
                className="font-display text-4xl font-extrabold leading-none tracking-tight focus:outline-none sm:text-[56px]"
                id="plan-heading"
                tabIndex={-1}
              >
                {mealName}
              </h1>
              <div className="flex flex-wrap gap-2">
                {match && <PriceTag tone={match.tone}>{match.label}</PriceTag>}
                {outcome && <PriceTag tone={outcome.tone}>{outcome.label}</PriceTag>}
                {estimated && <PriceTag tone="warn">Some nutrition estimated</PriceTag>}
                {cost !== null && (
                  <PriceTag className="font-mono" tone="accent">
                    About {formatCurrency(cost)} to shop
                  </PriceTag>
                )}
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
              <Icon as={Info} className="mt-0.5" />
              <span>
                {estimated.estimated} of {estimated.of} ingredients use estimated nutrition from
                local tables, so these numbers are approximate.
                {outcome &&
                  ' “On target” is measured against those same tables, so treat it as a guide.'}
              </span>
            </p>
          )}
          {feedback?.off && (
            <p className="relative mt-4 text-sm text-on-ink-muted" role="status">
              {HOSTED_FEEDBACK_MESSAGE}
            </p>
          )}
        </div>
      </section>

      <div className={`${pageShell} flex flex-wrap items-start gap-6 py-6`}>
        <div className="flex min-w-0 flex-[3_1_560px] flex-col gap-6">
          {tabs.length > 1 && (
            <Tabs
              active={tab}
              idPrefix="plan"
              label="Plan sections"
              onChange={(next) => setChosen({ plan: planKey, tab: next })}
              tabs={tabs}
            />
          )}
          <div
            aria-labelledby={tabs.length > 1 ? `plan-tab-${tab}` : undefined}
            className="flex flex-col gap-6"
            id="plan-panel"
            role={tabs.length > 1 ? 'tabpanel' : undefined}
          >
            {tab === 'overview' && (
              <>
              {(energy || split || outcome) && (
                <section aria-labelledby="nutrition-heading" className={card}>
                  <h2 className={sectionHeading} id="nutrition-heading">
                    <Icon as={Flame} size="lg" tone="light" />
                    Nutrition
                  </h2>
                  {energy && (
                    <div className="mt-5 flex flex-wrap items-center gap-8">
                      <CalorieRing target={energy.target} total={energy.total} />
                      {split && <MacroDonut grams={energy.grams} legend={false} split={split} />}
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
                          <RangeBars grams={energy?.grams} split={split} />
                        </div>
                        {outcome && (
                          <p className="mt-3 text-sm text-muted">
                            The shaded band is the recommended range and the marker is this meal. The tag at
                        the top of the page gives the overall result.
                          </p>
                        )}
                      </>
                    ) : (
                      <p className="mt-3 text-sm text-muted">This response has no nutrition to split.</p>
                    )}
                  </section>
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
                          className="inline-flex min-h-[48px] items-center gap-2 rounded-2xl bg-surface px-4 font-semibold text-ink hover:ring-2 hover:ring-cobalt focus:outline-none focus-visible:ring-2 focus-visible:ring-ink disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={runnerUpDisabled}
                          onClick={() => onPlanRunnerUp(meal.name)}
                          type="button"
                        >
                          {meal.name}
                          <Icon as={ArrowRight} size="sm" />
                        </button>
                      </li>
                    ))}
                  </ul>
                  <p className="mt-2.5 text-sm text-success-fg">
                    Choosing one plans that meal for you, sized the same way.
                  </p>
                </section>
              )}

              </>
            )}
            {tab === 'ingredients' && (
                <section aria-labelledby="sources-heading" className={card}>
                  <h2 className={sectionHeading} id="sources-heading">
                    <Icon as={PieChart} size="lg" tone="light" />
                    Where the calories come from
                  </h2>
                  <p className="mb-4 mt-1 text-sm text-muted">
                    Each ingredient&rsquo;s share of this meal, with its served portion and where its
                    nutrition numbers come from.
                  </p>
                  <CalorieSources items={items} />
                </section>
            )}
            {tab === 'made' && (
              <section aria-labelledby="made-heading" className={card}>
                <h2 className={sectionHeading} id="made-heading">
                  <Icon as={BookOpenCheck} size="lg" tone="light" />
                  How this plan was made
                </h2>
                <p className="mt-1 text-sm text-muted">
                  The service&rsquo;s own notes on how it sized and checked this meal.
                </p>
                <ol className="mt-4 divide-y divide-dashed divide-line">
                  {notes.map((note, index) => (
                    <li className="flex items-start gap-3 py-3 text-[15px] text-ink" key={note}>
                      <span
                        aria-hidden="true"
                        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-tint font-mono text-xs font-bold text-cobalt"
                      >
                        {index + 1}
                      </span>
                      <span className="pt-0.5">{note}</span>
                    </li>
                  ))}
                </ol>
              </section>
            )}
          </div>
        </div>

        <aside
          aria-label="Shopping and rating"
          className="flex min-w-0 flex-[2_1_340px] flex-col gap-6"
        >
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
