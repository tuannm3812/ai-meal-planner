import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const fb = vi.hoisted(() => {
  const auth = { currentUser: null, authStateReady: vi.fn(() => Promise.resolve()) }
  const anonymous = { uid: 'anon-1', isAnonymous: true, getIdToken: vi.fn(() => Promise.resolve('tok-anon')) }
  return {
    auth,
    anonymous,
    app: { initializeApp: vi.fn(() => ({})) },
    module: {
      getAuth: vi.fn(() => auth),
      onAuthStateChanged: vi.fn((_, callback) => {
        callback(auth.currentUser)
        return () => {}
      }),
      signInAnonymously: vi.fn(async () => {
        auth.currentUser = anonymous
        return { user: anonymous }
      }),
      GoogleAuthProvider: Object.assign(vi.fn(), { credentialFromError: vi.fn(() => 'cred') }),
      linkWithPopup: vi.fn(),
      signInWithPopup: vi.fn(),
      signInWithCredential: vi.fn(),
      signOut: vi.fn(() => Promise.resolve()),
      deleteUser: vi.fn(() => Promise.resolve()),
      reauthenticateWithPopup: vi.fn(() => Promise.resolve()),
    },
  }
})
vi.mock('firebase/app', () => fb.app)
vi.mock('firebase/auth', () => fb.module)

const GOOGLE = { uid: 'g-1', isAnonymous: false, displayName: 'Sam', email: 's@x.y', photoURL: null }

async function load({ enabled = true } = {}) {
  vi.resetModules()
  vi.stubEnv('VITE_FIREBASE_API_KEY', enabled ? 'key' : '')
  vi.stubEnv('VITE_FIREBASE_AUTH_DOMAIN', 'demo.firebaseapp.com')
  vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'demo')
  return import('./firebase')
}

describe('firebase accounts', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fb.auth.currentUser = null
  })
  afterEach(() => vi.unstubAllEnvs())

  it('is off without the web config, and then sends nothing', async () => {
    const firebase = await load({ enabled: false })
    const seen = vi.fn()

    expect(firebase.accountsEnabled).toBe(false)
    expect(await firebase.apiIdentity()).toEqual({ headers: {}, uid: null })
    firebase.watchUser(seen)
    expect(seen).toHaveBeenCalledWith(null)
    await firebase.signOutUser()
    await firebase.deleteSignIn()
    expect(fb.app.initializeApp).not.toHaveBeenCalled()
  })

  it('signs a first caller in anonymously, once, and sends its token', async () => {
    const firebase = await load()

    const [one, two] = await Promise.all([firebase.apiIdentity(), firebase.apiIdentity()])

    expect(one).toEqual({ headers: { Authorization: 'Bearer tok-anon' }, uid: 'anon-1' })
    expect(two.uid).toBe('anon-1')
    expect(fb.module.signInAnonymously).toHaveBeenCalledTimes(1)
  })

  it('describes only what the app shows, and watches for changes', async () => {
    const firebase = await load()
    fb.auth.currentUser = GOOGLE
    const seen = vi.fn()

    firebase.watchUser(seen)

    expect(seen).toHaveBeenCalledWith({
      uid: 'g-1',
      isAnonymous: false,
      name: 'Sam',
      email: 's@x.y',
      photoUrl: null,
    })
    expect(firebase.describeUser(null)).toBeNull()
  })

  it('links an anonymous visitor to Google, keeping the uid', async () => {
    const firebase = await load()
    fb.auth.currentUser = fb.anonymous
    fb.module.linkWithPopup.mockResolvedValueOnce({ user: { ...GOOGLE, uid: 'anon-1' } })

    expect((await firebase.signInWithGoogle()).uid).toBe('anon-1')
  })

  it('signs into an existing Google account when linking finds one', async () => {
    const firebase = await load()
    fb.auth.currentUser = fb.anonymous
    fb.module.linkWithPopup.mockRejectedValueOnce({ code: 'auth/credential-already-in-use' })
    fb.module.signInWithCredential.mockResolvedValueOnce({ user: GOOGLE })

    expect((await firebase.signInWithGoogle()).uid).toBe('g-1')
    expect(fb.module.signInWithCredential).toHaveBeenCalledWith(fb.auth, 'cred')
  })

  it('passes on any other linking error', async () => {
    const firebase = await load()
    fb.auth.currentUser = fb.anonymous
    fb.module.linkWithPopup.mockRejectedValueOnce({ code: 'auth/popup-closed-by-user' })

    await expect(firebase.signInWithGoogle()).rejects.toEqual({ code: 'auth/popup-closed-by-user' })
  })

  it('uses a plain popup when nobody is signed in', async () => {
    const firebase = await load()
    fb.module.signInWithPopup.mockResolvedValueOnce({ user: GOOGLE })

    expect((await firebase.signInWithGoogle()).email).toBe('s@x.y')
  })

  it('signs out, and deletes the sign-in, asking again when Firebase wants a recent one', async () => {
    const firebase = await load()
    fb.auth.currentUser = GOOGLE
    fb.module.deleteUser.mockRejectedValueOnce({ code: 'auth/requires-recent-login' })

    await firebase.signOutUser()
    await firebase.deleteSignIn()

    expect(fb.module.signOut).toHaveBeenCalled()
    expect(fb.module.reauthenticateWithPopup).toHaveBeenCalled()
    expect(fb.module.deleteUser).toHaveBeenCalledTimes(2)
  })

  it('passes on any other delete error', async () => {
    const firebase = await load()
    fb.auth.currentUser = GOOGLE
    fb.module.deleteUser.mockRejectedValueOnce({ code: 'auth/network-request-failed' })

    await expect(firebase.deleteSignIn()).rejects.toEqual({ code: 'auth/network-request-failed' })
  })
})
