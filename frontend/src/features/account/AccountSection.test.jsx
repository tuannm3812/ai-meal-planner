import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

// The Firebase module is replaced: these test the app's account behaviour
// (DEC-43), not Firebase. `emit` plays Firebase announcing a user.
const auth = vi.hoisted(() => {
  const state = { listener: null }
  return {
    state,
    emit: (user) => state.listener?.(user),
    module: {
      accountsEnabled: true,
      apiIdentity: vi.fn(() => Promise.resolve({ headers: {}, uid: null })),
      watchUser: vi.fn((callback) => {
        state.listener = callback
        callback(null)
        return () => {}
      }),
      signInWithGoogle: vi.fn(),
      signOutUser: vi.fn(() => Promise.resolve()),
      deleteSignIn: vi.fn(() => Promise.resolve()),
    },
  }
})
vi.mock('../../auth/firebase', () => auth.module)

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
    put: vi.fn(() => Promise.resolve({ data: {} })),
    delete: vi.fn(() => Promise.resolve({ data: { status: 'deleted' } })),
  },
}))

import axios from 'axios'

import { loadStored } from '../../app/storage'
import { DEFAULT_PROFILE } from '../profile/profile'
import { STORED, renderApp } from '../../test/renderApp'

const GOOGLE_USER = {
  uid: 'uid-1',
  isAnonymous: false,
  name: 'Sam Cook',
  email: 'sam@example.com',
  photoUrl: null,
}

function signInAs(user) {
  auth.module.signInWithGoogle.mockImplementationOnce(async () => {
    act(() => auth.emit(user))
    return user
  })
}

describe('accounts on the Profile page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('offers Google sign-in to a visitor who has not signed in', () => {
    renderApp({ route: '/profile', stored: STORED })
    expect(screen.getByRole('heading', { name: 'Your account' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Sign in with Google' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument()
  })

  it('saves this device’s details to a new account on first sign-in', async () => {
    const user = userEvent.setup()
    axios.get.mockImplementation((url) =>
      url.endsWith('/me/profile')
        ? Promise.reject({ response: { status: 404 } })
        : Promise.resolve({ data: { items: [] } }),
    )
    signInAs(GOOGLE_USER)
    renderApp({ route: '/profile', stored: STORED })

    await user.click(screen.getByRole('button', { name: 'Sign in with Google' }))

    expect(await screen.findByText(/Your details are saved to your account/)).toBeInTheDocument()
    expect(axios.put).toHaveBeenCalledWith(
      expect.stringMatching(/\/me\/profile$/),
      { profile: DEFAULT_PROFILE, location: 'Earlwood, NSW' },
    )
    expect(screen.getByText(/Signed in as Sam Cook \(sam@example.com\)/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Sign in' })).not.toBeInTheDocument()
  })

  it('loads an existing account’s details onto this device', async () => {
    const user = userEvent.setup()
    axios.get.mockImplementation((url) =>
      url.endsWith('/me/profile')
        ? Promise.resolve({
            data: { profile: { goal: 'lose', age: '52' }, location: 'Ashfield', updated_at: 'x' },
          })
        : Promise.resolve({ data: { items: [] } }),
    )
    signInAs(GOOGLE_USER)
    renderApp({ route: '/profile', stored: STORED })

    await user.click(screen.getByRole('button', { name: 'Sign in with Google' }))

    expect(await screen.findByText(/account’s saved details are now on this device/)).toBeInTheDocument()
    expect(loadStored().profile).toMatchObject({ goal: 'lose', age: '52' })
    expect(loadStored().location).toBe('Ashfield')
  })

  it('says so when sign-in does not finish, but not when the window is closed', async () => {
    const user = userEvent.setup()
    auth.module.signInWithGoogle.mockRejectedValueOnce({ code: 'auth/popup-closed-by-user' })
    renderApp({ route: '/profile', stored: STORED })

    await user.click(screen.getByRole('button', { name: 'Sign in with Google' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Sign in with Google' })).toBeEnabled())
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()

    auth.module.signInWithGoogle.mockRejectedValueOnce({ code: 'auth/network-request-failed' })
    await user.click(screen.getByRole('button', { name: 'Sign in with Google' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Sign-in did not finish')
  })

  it('deletes the account only after a confirmation, then forgets this device', async () => {
    const user = userEvent.setup()
    renderApp({ route: '/profile', stored: STORED })
    act(() => auth.emit(GOOGLE_USER))

    await user.click(screen.getByRole('button', { name: 'Delete my account and data' }))
    expect(axios.delete).not.toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: 'Keep my account' }))
    await user.click(screen.getByRole('button', { name: 'Delete my account and data' }))
    await user.click(screen.getByRole('button', { name: 'Yes, delete everything' }))

    await waitFor(() => expect(auth.module.deleteSignIn).toHaveBeenCalled())
    expect(axios.delete).toHaveBeenCalledWith(expect.stringMatching(/\/me$/))
    expect(loadStored()).toBeNull()
  })

  it('keeps everything when the server could not delete the account', async () => {
    const user = userEvent.setup()
    axios.delete.mockRejectedValueOnce({ response: { status: 500 } })
    renderApp({ route: '/profile', stored: STORED })
    act(() => auth.emit(GOOGLE_USER))

    await user.click(screen.getByRole('button', { name: 'Delete my account and data' }))
    await user.click(screen.getByRole('button', { name: 'Yes, delete everything' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('nothing was removed')
    expect(auth.module.deleteSignIn).not.toHaveBeenCalled()
    expect(loadStored()).not.toBeNull()
  })

  it('signs out and forgets this device', async () => {
    const user = userEvent.setup()
    renderApp({ route: '/profile', stored: STORED })
    act(() => auth.emit(GOOGLE_USER))

    await user.click(screen.getByRole('button', { name: 'Sign out' }))

    await waitFor(() => expect(auth.module.signOutUser).toHaveBeenCalled())
    expect(loadStored()).toBeNull()
  })
})
