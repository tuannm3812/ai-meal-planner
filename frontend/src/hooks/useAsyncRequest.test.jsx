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
