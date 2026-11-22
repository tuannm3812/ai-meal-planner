import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { STORAGE_KEY, clearStored, loadStored, saveStored } from './storage'

const VALUE = { userId: 'web-1', profile: { age: '34' }, location: 'Earlwood, NSW' }

describe('storage', () => {
  beforeEach(() => localStorage.clear())
  afterEach(() => vi.restoreAllMocks())

  it('round-trips the three remembered values under one key', () => {
    expect(saveStored(VALUE)).toBe(true)
    expect(Object.keys(localStorage)).toEqual([STORAGE_KEY])
    expect(loadStored()).toEqual(VALUE)
  })

  it('stores nothing beyond the user ID, profile and location', () => {
    saveStored({ ...VALUE, plan: { secret: true } })
    expect(Object.keys(JSON.parse(localStorage.getItem(STORAGE_KEY)))).toEqual([
      'userId',
      'profile',
      'location',
    ])
  })

  it('reads nothing from a missing, malformed or foreign value', () => {
    expect(loadStored()).toBeNull()
    localStorage.setItem(STORAGE_KEY, '{not json')
    expect(loadStored()).toBeNull()
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ profile: {} }))
    expect(loadStored()).toBeNull()
  })

  it('keeps working when storage is blocked', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    expect(loadStored()).toBeNull()
    expect(saveStored(VALUE)).toBe(false)
    expect(clearStored()).toBe(false)
  })

  it('forgets everything', () => {
    saveStored(VALUE)
    expect(clearStored()).toBe(true)
    expect(loadStored()).toBeNull()
  })
})
