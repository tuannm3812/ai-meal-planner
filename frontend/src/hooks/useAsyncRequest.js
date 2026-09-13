import { useCallback, useState } from 'react'

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
export function useAsyncRequest(requestFn, fallbackMessage = 'Something went wrong.') {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const run = useCallback(
    async (...args) => {
      setError('')
      setIsLoading(true)
      try {
        const result = await requestFn(...args)
        setData(result)
      } catch (requestError) {
        setError(requestError?.response?.data?.detail || fallbackMessage)
      } finally {
        setIsLoading(false)
      }
    },
    [requestFn, fallbackMessage],
  )

  const reset = useCallback(() => {
    setData(null)
    setError('')
  }, [])

  return { data, error, isLoading, run, reset }
}
