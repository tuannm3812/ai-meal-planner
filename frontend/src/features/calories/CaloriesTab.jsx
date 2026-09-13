import { useState } from 'react'

import { predictCalorieExpenditure } from '../../api/mealPlanner'
import { useAsyncRequest } from '../../hooks/useAsyncRequest'
import { parseCommaList } from '../../lib/format'
import EmptyState from '../../components/ui/EmptyState'
import ErrorBanner from '../../components/ui/ErrorBanner'
import InputField from '../../components/ui/InputField'
import SelectField from '../../components/ui/SelectField'
import SubmitButton from '../../components/ui/SubmitButton'
import CalorieResult from './CalorieResult'

const GOAL_OPTIONS = [
  { value: 'maintain', label: 'Maintain' },
  { value: 'weight_loss', label: 'Weight loss' },
  { value: 'muscle_gain', label: 'Muscle gain' },
]

const SEX_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
]

function CaloriesTab() {
  const [age, setAge] = useState(28)
  const [sex, setSex] = useState('male')
  const [heightCm, setHeightCm] = useState(180)
  const [weightKg, setWeightKg] = useState(80)
  const [activityMultiplier, setActivityMultiplier] = useState(1.55)
  const [durationMinutes, setDurationMinutes] = useState(30)
  const [heartRateBpm, setHeartRateBpm] = useState(100)
  const [bodyTempC, setBodyTempC] = useState(37)
  const [goal, setGoal] = useState('maintain')
  const [healthConditionsInput, setHealthConditionsInput] = useState('')
  const {
    data: result,
    error,
    isLoading,
    run: requestExpenditure,
    reset: clearResult,
  } = useAsyncRequest(
    predictCalorieExpenditure,
    'Could not predict calorie expenditure. Check that the FastAPI backend is running on port 8000.',
  )

  const handleSubmit = async (event) => {
    event.preventDefault()
    clearResult()
    await requestExpenditure({
      age: Number(age),
      sex,
      height_cm: Number(heightCm),
      weight_kg: Number(weightKg),
      activity_multiplier: Number(activityMultiplier),
      duration_minutes: Number(durationMinutes),
      heart_rate_bpm: Number(heartRateBpm),
      body_temp_c: Number(bodyTempC),
      goal,
      health_conditions: parseCommaList(healthConditionsInput),
    })
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <aside className="rounded-2xl border border-gray-100 bg-white p-6 shadow-md lg:sticky lg:top-6 lg:self-start">
        <h2 className="text-lg font-semibold text-gray-900">Calorie Expenditure</h2>
        <p className="mt-1 text-sm leading-6 text-gray-500">
          Calls the promoted Kaggle calorie model artifact.
        </p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Age"
              max={120}
              min={1}
              onChange={(event) => setAge(event.target.value)}
              type="number"
              value={age}
            />
            <SelectField label="Sex" onChange={(event) => setSex(event.target.value)} options={SEX_OPTIONS} value={sex} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Height (cm)"
              max={260}
              min={80}
              onChange={(event) => setHeightCm(event.target.value)}
              type="number"
              value={heightCm}
            />
            <InputField
              label="Weight (kg)"
              max={350}
              min={20}
              onChange={(event) => setWeightKg(event.target.value)}
              type="number"
              value={weightKg}
            />
          </div>
          <InputField
            helperText="Typical values: 1.2 sedentary, 1.375 light, 1.55 moderate, 1.725 very active, 1.9 extra active."
            label="Activity multiplier"
            max={2.5}
            min={1.0}
            onChange={(event) => setActivityMultiplier(event.target.value)}
            step={0.025}
            type="number"
            value={activityMultiplier}
          />
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Duration (min)"
              max={600}
              min={1}
              onChange={(event) => setDurationMinutes(event.target.value)}
              type="number"
              value={durationMinutes}
            />
            <InputField
              label="Heart rate (bpm)"
              max={240}
              min={20}
              onChange={(event) => setHeartRateBpm(event.target.value)}
              type="number"
              value={heartRateBpm}
            />
          </div>
          <InputField
            label="Body temp (C)"
            max={45}
            min={30}
            onChange={(event) => setBodyTempC(event.target.value)}
            step={0.1}
            type="number"
            value={bodyTempC}
          />
          <SelectField label="Goal" onChange={(event) => setGoal(event.target.value)} options={GOAL_OPTIONS} value={goal} />
          <InputField
            helperText="Comma separated, e.g. 'diabetes, hypertension'."
            label="Health conditions"
            onChange={(event) => setHealthConditionsInput(event.target.value)}
            value={healthConditionsInput}
          />

          <SubmitButton
            disabled={isLoading}
            idleLabel="Predict Expenditure"
            isLoading={isLoading}
            loadingLabel="Predicting..."
          />
        </form>

        {error && <div className="mt-5"><ErrorBanner>{error}</ErrorBanner></div>}
      </aside>

      <div className="grid gap-6">
        {!result && (
          <EmptyState
            idleBody="Fill in the biometrics on the left to estimate daily calorie expenditure and a meal budget."
            idleTitle="Predict your calorie expenditure"
            isLoading={isLoading}
            loadingBody="Running the calorie forecasting model."
            loadingTitle="Predicting expenditure"
          />
        )}

        {result && <CalorieResult result={result} />}
      </div>
    </div>
  )
}

export default CaloriesTab
