import { screen } from '@testing-library/react'

// Moving through the flow the way a person does: by the step indicator.
export const goToStep = (user, name) => user.click(screen.getByRole('button', { name }))

export const cravingInput = () => screen.getByLabelText(/Your craving/i)
export const planButton = () => screen.getByRole('button', { name: 'Plan my meal' })

// Types a craving on step 2 (opening it if needed) and plans.
export async function planMeal(user, craving) {
  if (!screen.queryByLabelText(/Your craving/i)) await goToStep(user, '2 · Craving')
  await user.clear(cravingInput())
  await user.type(cravingInput(), craving)
  await user.click(planButton())
}
