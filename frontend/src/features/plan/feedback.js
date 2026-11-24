// What POST /meal-feedback is sent for a plan (MealFeedbackRequest).
export function feedbackPayload(plan, userId, values) {
  return {
    user_id: userId,
    request_id: plan.request_id,
    meal_id: plan?.meal_plan?.retrieval?.selected_meal_id ?? null,
    meal_name: plan?.meal_plan?.meal_definition?.structured_meal_name ?? 'Untitled meal',
    ...values,
  }
}

export const HOSTED_FEEDBACK_MESSAGE =
  'Saving, ratings and history are off on this hosted server, which keeps nothing between requests.'

// A hosted API answers 501 to anything that would store state (G6).
export const isNotImplemented = (error) => error?.response?.status === 501

export function feedbackErrorMessage(error) {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' && detail
    ? detail
    : 'Could not save that. Check your connection and try again.'
}
