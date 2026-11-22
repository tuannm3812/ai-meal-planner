// What the app remembers on this device (DEC-36): the opaque user ID, the
// profile and where the person shops. Nothing else: no plans, ratings or
// ticks. Storage can be blocked or full, so every call is guarded and the app
// still works for the visit without it.
export const STORAGE_KEY = 'aimp.v1'

export function loadStored() {
  try {
    const raw = globalThis.localStorage?.getItem(STORAGE_KEY)
    if (!raw) return null
    const value = JSON.parse(raw)
    if (!value || typeof value !== 'object' || typeof value.userId !== 'string') return null
    return { userId: value.userId, profile: value.profile ?? null, location: value.location ?? null }
  } catch {
    return null
  }
}

export function saveStored({ userId, profile, location }) {
  try {
    globalThis.localStorage.setItem(STORAGE_KEY, JSON.stringify({ userId, profile, location }))
    return true
  } catch {
    return false
  }
}

export function clearStored() {
  try {
    globalThis.localStorage.removeItem(STORAGE_KEY)
    return true
  } catch {
    return false
  }
}
