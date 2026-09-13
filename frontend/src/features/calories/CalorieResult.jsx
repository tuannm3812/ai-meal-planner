import SectionCard from '../../components/ui/SectionCard'
import StatCard from '../../components/ui/StatCard'
import SuccessBanner from '../../components/ui/SuccessBanner'

function CalorieResult({ result }) {
  return (
    <>
      <SuccessBanner>Calorie expenditure predicted using {result.model_version}.</SuccessBanner>

      <SectionCard eyebrow="Forecast" title="Calorie Expenditure">
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard
            dot="bg-amber-400"
            label="Daily expenditure"
            value={`${Number(result.estimated_daily_expenditure_kcal).toLocaleString()} kcal`}
          />
          <StatCard
            dot="bg-sky-500"
            label="Meal budget"
            value={`${Number(result.meal_calorie_budget_kcal).toLocaleString()} kcal`}
          />
          <StatCard
            dot="bg-violet-500"
            label="Confidence"
            value={`${Math.round(result.confidence * 100)}%`}
          />
        </div>
      </SectionCard>

      {result.warnings?.length > 0 && (
        <SectionCard eyebrow="Notes" title="Warnings">
          <ul className="space-y-2 text-sm text-gray-600">
            {result.warnings.map((warning) => (
              <li className="rounded-lg bg-amber-50 px-3 py-2 text-amber-800" key={warning}>
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
