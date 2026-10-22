import { useEffect, useState } from 'react'

import { describeFailure } from './failures'

// One failed meal request, worded by its status. A retry is offered only when
// it can help; after a 429 it waits out the pause first. Remount (key) per
// failure so each one starts its own pause.
function FailurePanel({ failure, message, onRetry, canRetry = true }) {
  const described = describeFailure(failure)
  const pause = described.retry ?? 0
  const [waiting, setWaiting] = useState(pause > 0)

  useEffect(() => {
    if (pause <= 0) return undefined
    const timer = setTimeout(() => setWaiting(false), pause * 1000)
    return () => clearTimeout(timer)
  }, [pause])

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
          disabled={waiting || !canRetry}
          onClick={onRetry}
          type="button"
        >
          Try again
        </button>
      )}
      {offerRetry && waiting && (
        <p className="mt-2">You can try again in about {pause} seconds.</p>
      )}
    </div>
  )
}

export default FailurePanel
