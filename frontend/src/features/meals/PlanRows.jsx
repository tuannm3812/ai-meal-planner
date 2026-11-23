import { Link } from 'react-router-dom'

import Icon from '../../components/icons/Icon'
import { ArrowRight } from '../../components/icons/glyphs'
import DishIllustration from '../../components/illustrations/DishIllustration'
import PriceTag from '../../components/ui/PriceTag'
import { MACROS } from '../plan/plan'
import { byDay } from './meals'

// Past plans as a dated list: a heading per day, then one row per plan with
// its drawing, craving, calories against the target, macro strip and result.
function PlanRows({ meals }) {
  return (
    <div className="flex flex-col gap-7">
      {byDay(meals).map((group) => (
        <section aria-labelledby={`day-${group.key}`} key={group.key}>
          <h2
            className="flex items-center gap-3 font-mono text-xs font-bold uppercase tracking-widest text-cobalt"
            id={`day-${group.key}`}
          >
            {group.label}
            <span aria-hidden="true" className="h-px flex-1 border-t border-dashed border-line" />
            <span className="text-muted">
              {group.meals.length} {group.meals.length === 1 ? 'plan' : 'plans'}
            </span>
          </h2>
          <ul className="mt-3 flex flex-col gap-3">
            {group.meals.map((meal) => (
              <li key={meal.requestId}>
                <Link
                  className="grid grid-cols-[72px_minmax(0,1fr)] items-center gap-x-4 gap-y-3 rounded-3xl bg-surface p-4 text-ink hover:ring-2 hover:ring-cobalt focus:outline-none focus-visible:ring-2 focus-visible:ring-ink md:grid-cols-[88px_minmax(0,1.3fr)_minmax(0,1fr)_auto]"
                  to={`/plans/${encodeURIComponent(meal.requestId)}`}
                >
                  <DishIllustration
                    className="h-[72px] w-full rounded-2xl bg-tint md:h-[80px]"
                    mealName={meal.name}
                    type={meal.dish ?? undefined}
                  />
                  <span className="flex min-w-0 flex-col gap-1">
                    <span className="text-lg font-semibold">{meal.name ?? 'Untitled meal'}</span>
                    {meal.craving && (
                      <span className="text-[13px] text-muted">For &ldquo;{meal.craving}&rdquo;</span>
                    )}
                    <span className="mt-1 flex flex-wrap gap-2">
                      {meal.kcal !== null && (
                        <PriceTag className="font-mono" tone="accent">
                          {meal.target === null ? `${meal.kcal} kcal` : `${meal.kcal} of ${meal.target} kcal`}
                        </PriceTag>
                      )}
                      {meal.outcome && <PriceTag tone={meal.outcome.tone}>{meal.outcome.label}</PriceTag>}
                      {meal.status === 'fallback' && <PriceTag tone="warn">Standard meal</PriceTag>}
                    </span>
                  </span>
                  {meal.split ? (
                    <span className="col-span-2 flex flex-col gap-1.5 md:col-span-1">
                      <span aria-hidden="true" className="flex h-2.5 overflow-hidden rounded-full">
                        {MACROS.map((macro) => (
                          <span className={macro.bar} key={macro.key} style={{ width: `${meal.split[macro.key]}%` }} />
                        ))}
                      </span>
                      <span className="text-[13px] text-muted">
                        {MACROS.map((macro) => `${macro.label} ${Math.round(meal.split[macro.key])}%`).join(' · ')}
                      </span>
                    </span>
                  ) : (
                    <span className="hidden md:block" />
                  )}
                  <Icon as={ArrowRight} className="hidden md:block" tone="light" />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  )
}

export default PlanRows
