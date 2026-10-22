import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { useAsyncRequest } from './useAsyncRequest'

describe('useAsyncRequest', () => {
  it('starts idle', () => {
    const { result } = renderHook(() => useAsyncRequest(vi.fn()))
    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBe('')
  })

  it('stores the resolved value', async () => {
    const request = vi.fn(() => Promise.resolve({ ok: true }))
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run('arg')
    })
    expect(request).toHaveBeenCalledWith('arg')
    expect(result.current.data).toEqual({ ok: true })
    expect(result.current.error).toBe('')
    expect(result.current.isLoading).toBe(false)
  })

  it('stores a string error on rejection and does not throw', async () => {
    const request = vi.fn(() => Promise.reject(new Error('boom')))
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run()
    })
    await waitFor(() => expect(result.current.error).not.toBe(''))
    expect(typeof result.current.error).toBe('string')
    expect(result.current.isLoading).toBe(false)
  })

  it('clears state on reset', async () => {
    const request = vi.fn(() => Promise.resolve({ ok: true }))
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run()
    })
    act(() => {
      result.current.reset()
    })
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBe('')
  })
})


describe('useAsyncRequest error messages', () => {
  it("prefers the backend's detail over the fallback", async () => {
    const request = vi.fn(() =>
      Promise.reject({ response: { data: { detail: 'from the backend' } } }),
    )
    const { result } = renderHook(() => useAsyncRequest(request, 'my fallback'))
    await act(async () => {
      await result.current.run()
    })
    expect(result.current.error).toBe('from the backend')
  })

  it("uses the caller's fallback when there is no response", async () => {
    const request = vi.fn(() => Promise.reject(new Error('Network Error')))
    const { result } = renderHook(() => useAsyncRequest(request, 'my fallback'))
    await act(async () => {
      await result.current.run()
    })
    // Not error.message - each tab has its own sentence and must keep it.
    expect(result.current.error).toBe('my fallback')
  })
})

describe('useAsyncRequest validation errors', () => {
  it('shows the fallback for a list detail and keeps the list for the form', async () => {
    // A FastAPI 422 sends a list of field errors; rendering that list as text
    // would crash React, so the banner gets the fallback sentence instead.
    const detail = [{ loc: ['body', 'age'], msg: 'Input should be less than or equal to 120' }]
    const request = vi.fn(() => Promise.reject({ response: { status: 422, data: { detail } } }))
    const { result } = renderHook(() => useAsyncRequest(request, 'my fallback'))
    await act(async () => {
      await result.current.run()
    })
    expect(result.current.error).toBe('my fallback')
    expect(result.current.errorDetail).toEqual(detail)
  })

  it('clears the kept detail on the next run and on reset', async () => {
    const request = vi
      .fn()
      .mockRejectedValueOnce({ response: { data: { detail: [{ loc: ['body', 'age'] }] } } })
      .mockResolvedValueOnce({ ok: true })
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run()
    })
    expect(result.current.errorDetail).not.toBeNull()
    await act(async () => {
      await result.current.run()
    })
    expect(result.current.errorDetail).toBeNull()
  })
})
