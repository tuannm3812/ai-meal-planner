import { useEffect, useState } from 'react'

import { describeFailure } from './failures'

// The pause a failure asks for (a 429's Retry-After, or the default), as one
// deadline the whole screen obeys: the plan button, Enter in the form and
// "Try again" all wait until it passes.
export function useRetryPause(failure) {
  const pause = failure ? (describeFailure(failure).retry ?? 0) : 0
  const until = pause > 0 && typeof failure.at === 'number' ? failure.at + pause * 1000 : null
  // Only ever compared with `until`, and moved forward when the pause ends,
  // so a failure that arrives later always starts out paused.
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (until === null) return undefined
    const timer = setTimeout(() => setNow(Date.now()), Math.max(0, until - Date.now()))
    return () => clearTimeout(timer)
  }, [until])

  const active = until !== null && now < until
  return { active, seconds: pause }
}
