import { describeFailure } from './failures'

// One failed meal request, worded by its status. A retry is offered only when
// it can help. The pause after a 429 belongs to the screen (useRetryPause),
// which holds every way of sending; this panel only shows it.
function FailurePanel({ failure, message, onRetry, canRetry = true, pause }) {
  const described = describeFailure(failure)
  const offerRetry = described.retry !== null && onRetry
  return (
    <div
      className="rounded-[14px] border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-800"
      role="alert"
    >
      <p className="font-semibold">{described.title}</p>
      <p>{message ?? described.body}</p>
      {offerRetry && (
        <button
          className="mt-3 min-h-[44px] rounded-xl bg-ink px-4 font-semibold text-white disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-600"
          disabled={!canRetry}
          onClick={onRetry}
          type="button"
        >
          Try again
        </button>
      )}
      {pause?.active && <p className="mt-2">You can try again in about {pause.seconds} seconds.</p>}
    </div>
  )
}

export default FailurePanel
