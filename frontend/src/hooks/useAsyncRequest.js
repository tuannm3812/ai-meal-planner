import { useCallback, useRef, useState } from 'react'

// Every tab repeats the same isLoading/error/data triple around a request.
// This hook holds that once. `run` never re-throws: a rejected request must
// leave the UI in a usable state (error set, isLoading cleared) rather than
// producing an unhandled rejection that the caller has to guard against.
//
// The error message mirrors the shape every tab already uses: prefer the
// backend's own `detail`, otherwise the caller's own fallback sentence. That
// second argument is what makes the hook adoptable at all - all four call
// sites differ ONLY in that sentence ("Could not generate a meal plan...",
// "Could not load saved meals...", and so on), so a hook with a hard-coded
// generic message would have silently changed user-facing text and none of
// them could have used it.
//
// Only a string `detail` is shown. A 422's detail is a list of field errors,
// which cannot be rendered as text; `errorDetail` keeps whatever the backend
// sent so a form can map those errors back to its fields. `failure` says what
// kind of failure it was (no response, or a status, code and Retry-After), so
// a screen can word each one and decide whether a retry can help.
//
// Only the latest request may settle the state. An answer to an earlier run,
// or to one `reset` has abandoned, is dropped when it arrives, so a slow
// response can never replace a newer one (the in-flight guard).
export function useAsyncRequest(requestFn, fallbackMessage = 'Something went wrong.') {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [errorDetail, setErrorDetail] = useState(null)
  const [failure, setFailure] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const latestRun = useRef(0)

  const run = useCallback(
    async (...args) => {
      latestRun.current += 1
      const thisRun = latestRun.current
      setError('')
      setErrorDetail(null)
      setFailure(null)
      setIsLoading(true)
      try {
        const result = await requestFn(...args)
        if (thisRun === latestRun.current) setData(result)
      } catch (requestError) {
        if (thisRun !== latestRun.current) return
        const detail = requestError?.response?.data?.detail
        setError(typeof detail === 'string' && detail ? detail : fallbackMessage)
        setErrorDetail(detail ?? null)
        const response = requestError?.response
        setFailure({
          reachable: Boolean(response),
          status: response?.status,
          code: response?.data?.code,
          detail: detail ?? null,
          retryAfter: response?.headers?.['retry-after'],
        })
      } finally {
        if (thisRun === latestRun.current) setIsLoading(false)
      }
    },
    [requestFn, fallbackMessage],
  )

  const reset = useCallback(() => {
    latestRun.current += 1
    setIsLoading(false)
    setData(null)
    setError('')
    setErrorDetail(null)
    setFailure(null)
  }, [])

  return { data, error, errorDetail, failure, isLoading, run, reset }
}
