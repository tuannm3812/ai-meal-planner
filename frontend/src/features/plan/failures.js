// What the plan screen says for each failure the meal request can return
// (docs/8_design.md §3.3, "States the screen must cover").

// Retry-After is not a CORS-safelisted header and the API does not expose it,
// so a browser on another origin usually cannot read it. This is the pause
// used then.
export const DEFAULT_RETRY_SECONDS = 10

export const UNREACHABLE_MESSAGE =
  'Could not generate a meal plan. Check that the FastAPI backend is running on port 8000.'

function retryAfterSeconds(header) {
  const seconds = Number(header)
  return Number.isFinite(seconds) && seconds > 0 ? Math.ceil(seconds) : DEFAULT_RETRY_SECONDS
}

// failure: { status, code, detail, retryAfter } from useAsyncRequest, where
// status is undefined when no response arrived at all.
export function describeFailure(failure) {
  const detail = typeof failure?.detail === 'string' && failure.detail ? failure.detail : null
  const status = failure?.status

  if (failure?.reachable === false) {
    return { title: 'Could not reach the meal planner', body: UNREACHABLE_MESSAGE, retry: 0 }
  }
  if (status === 401 || status === 403) {
    // The React client never sends a key (DEC-8), so retrying cannot help.
    return {
      title: 'This server needs an API key',
      body:
        status === 401
          ? 'It only answers requests that carry an API key, and this app does not send one. Run the API locally without API keys to use it here.'
          : 'The API key it received is not allowed to plan meals.',
      retry: null,
    }
  }
  if (status === 429) {
    return {
      title: 'Too many requests, try again shortly',
      body: 'The server is limiting how often plans can be made.',
      retry: retryAfterSeconds(failure.retryAfter),
    }
  }
  if (status === 502 && failure.code === 'unverified_required') {
    return {
      title: 'Nutrition could not be verified',
      body: detail ?? 'This server only serves plans with verified nutrition.',
      retry: null,
    }
  }
  if (status === 422) {
    // The screen maps a 422 back to its fields; sending it again unchanged
    // would be refused again.
    return {
      title: 'Check your details',
      body: detail ?? 'The service rejected this request.',
      retry: null,
    }
  }
  if (status === 503) {
    return {
      title: 'Planning is unavailable right now',
      body: detail ?? 'The meal planner is temporarily unavailable.',
      retry: 0,
    }
  }
  return {
    title: 'Could not make a plan',
    body: detail ?? UNREACHABLE_MESSAGE,
    retry: 0,
  }
}
