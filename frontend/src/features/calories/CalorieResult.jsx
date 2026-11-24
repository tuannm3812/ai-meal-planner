import Icon from '../../components/icons/Icon'
import { Flame, Scale, Utensils } from '../../components/icons/glyphs'
import Note from '../../components/ui/Note'
import { card } from '../../components/ui/styles'
import { mealSizeFromDaily, workoutNote } from '../plan/plan'

const whole = (value) => Math.round(Number(value)).toLocaleString('en-US')

// The estimate in the plan page's words: what you burn, the daily target for
// your goal, and one meal's share of it. The service calls the daily target
// `meal_calorie_budget_kcal`; it is the whole day's budget, not one meal.
function CalorieResult({ result }) {
  const daily = result.estimated_daily_expenditure_kcal
  const target = result.meal_calorie_budget_kcal
  const meal = mealSizeFromDaily(target)
  const tiles = [
    { glyph: Flame, label: 'You burn about', value: daily, unit: 'kcal a day' },
    { glyph: Scale, label: 'Daily target for your goal', value: target, unit: 'kcal a day' },
    { glyph: Utensils, label: 'One meal is sized to', value: meal, unit: 'kcal' },
  ]
  const workout = workoutNote(result)
  return (
    <section aria-labelledby="estimate-result" className={card}>
      <h2 className="font-display text-[20px] font-extrabold tracking-tight text-ink" id="estimate-result">
        Your estimate
      </h2>
      <dl className="mt-5 grid gap-4 sm:grid-cols-3">
        {tiles.map((tile) => (
          <div className="flex flex-col gap-2 rounded-2xl bg-ground p-4" key={tile.label}>
            <dt className="flex items-center gap-2 text-sm font-medium text-muted">
              <Icon as={tile.glyph} size="sm" tone="light" />
              {tile.label}
            </dt>
            <dd>
              <span className="block font-display text-[34px] font-extrabold leading-none text-ink">
                {tile.value === null ? '–' : whole(tile.value)}
              </span>
              <span className="mt-1 block text-sm text-muted">{tile.unit}</span>
            </dd>
          </div>
        ))}
      </dl>
      {workout && <Note className="mt-5">{workout}</Note>}
      {result.warnings?.map((warning) => (
        <p className="mt-3 rounded-xl bg-estimate-bg px-3.5 py-3 text-sm leading-6 text-estimate-fg" key={warning}>
          {warning}
        </p>
      ))}
      <p className="mt-4 text-sm text-muted">
        Model confidence {Math.round(Number(result.confidence) * 100)}%. A planning aid, not medical advice.
      </p>
    </section>
  )
}

export default CalorieResult
