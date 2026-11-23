import SectionCard from '../../components/ui/SectionCard'
import StatCard from '../../components/ui/StatCard'
import SuccessBanner from '../../components/ui/SuccessBanner'

function CalorieResult({ result }) {
  return (
    <>
      <SuccessBanner>Calorie expenditure predicted using {result.model_version}.</SuccessBanner>

      <SectionCard eyebrow="Estimate" title="Calories you burn">
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard
            label="Daily expenditure"
            value={`${Number(result.estimated_daily_expenditure_kcal).toLocaleString()} kcal`}
          />
          <StatCard
            label="Meal budget"
            value={`${Number(result.meal_calorie_budget_kcal).toLocaleString()} kcal`}
          />
          <StatCard
            label="Confidence"
            value={`${Math.round(result.confidence * 100)}%`}
          />
        </div>
      </SectionCard>

      {result.warnings?.length > 0 && (
        <SectionCard eyebrow="Notes" title="Warnings">
          <ul className="space-y-2 text-sm text-muted">
            {result.warnings.map((warning) => (
              <li className="rounded-lg bg-estimate-bg px-3 py-2 text-estimate-fg" key={warning}>
                {warning}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}
    </>
  )
}

export default CalorieResult
