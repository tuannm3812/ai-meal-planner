import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import { Calculator } from '../components/icons/glyphs'
import { pageShell, sectionHeading } from '../components/ui/styles'
import CaloriesTab from '../features/calories/CaloriesTab'

// The calorie model on its own (docs/8_design.md §7 question 7), now a tab of
// its own in the shell (DEC-44) instead of a button inside Profile.
// The estimate's goal names differ from the profile's.
const GOAL = { lose: 'weight_loss', maintain: 'maintain', gain: 'muscle_gain' }

function CaloriesPage() {
  const { hasProfile, profile } = usePlannerContext()
  const initial = hasProfile
    ? {
        age: profile.age,
        sex: profile.sex,
        heightCm: profile.heightCm,
        weightKg: profile.weightKg,
        activity: profile.activity,
        goal: GOAL[profile.goal],
      }
    : {}
  return (
    <main className={`${pageShell} flex flex-col gap-5 py-10`}>
      <div>
        <h1 className={`${sectionHeading} text-4xl`}>
          <Icon as={Calculator} size="lg" tone="light" />
          Calories
        </h1>
        <p className="mt-2 max-w-3xl text-muted">
          {hasProfile
            ? 'This starts from your details. Change anything to try it out; your profile stays as it is.'
            : 'Try the calorie model on its own, with any details.'}
        </p>
      </div>
      <CaloriesTab initial={initial} />
    </main>
  )
}

export default CaloriesPage
