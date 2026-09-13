import { useCallback, useState } from 'react'

// Every tab repeats the same isLoading/error/data triple around a request.
// This hook holds that once. `run` never re-throws: a rejected request must
// leave the UI in a usable state (error set, isLoading cleared) rather than
// producing an unhandled rejection that the caller has to guard against.
//
// The error message mirrors the shape the tabs already use when talking to
// the FastAPI backend via axios - prefer the backend's own detail message,
// then the JS error's message, then a generic fallback - so callers that
// adopt this hook keep a familiar, human-readable string instead of an
// Error object.
export function useAsyncRequest(requestFn) {
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
        const message =
          requestError?.response?.data?.detail ||
          requestError?.message ||
          'Something went wrong.'
        setError(message)
      } finally {
        setIsLoading(false)
      }
    },
    [requestFn],
  )

  const reset = useCallback(() => {
    setData(null)
    setError('')
  }, [])

  return { data, error, isLoading, run, reset }
}
