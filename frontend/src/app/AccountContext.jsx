import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'

import { deleteAccountData, fetchAccountProfile, saveAccountProfile } from '../api/mealPlanner'
import {
  accountsEnabled,
  deleteSignIn,
  signInWithGoogle,
  signOutUser,
  watchUser,
} from '../auth/firebase'
import { usePlannerContext } from './PlannerContext'

const AccountContext = createContext(null)

const SAVE_DELAY_MS = 800

// Google sign-in and the account's saved details (DEC-43). With accounts off
// (no Firebase config in the build) `enabled` is false and nothing here runs.
export function AccountProvider({ children }) {
  const planner = usePlannerContext()
  const [user, setUser] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [notice, setNotice] = useState(null)
  const signedIn = Boolean(user && !user.isAnonymous)
  const lastSaved = useRef(null)

  useEffect(() => (accountsEnabled ? watchUser(setUser) : undefined), [])

  // While signed in with Google, profile and location edits are saved to the
  // account a moment after the person stops typing.
  const { profile, location, hasProfile, profileIsValid } = planner
  useEffect(() => {
    if (!signedIn || !hasProfile || !profileIsValid) return undefined
    const snapshot = JSON.stringify({ profile, location })
    if (snapshot === lastSaved.current) return undefined
    const timer = setTimeout(() => {
      lastSaved.current = snapshot
      saveAccountProfile(profile, location).catch(() =>
        setError('Your details could not be saved to your account. They are still on this device.'),
      )
    }, SAVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [signedIn, hasProfile, profileIsValid, profile, location])

  // `failure` words an error; an Error thrown with its own message wins.
  const run = useCallback(async (work, failure) => {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await work()
    } catch (caught) {
      // Closing the Google window is a choice, not a failure.
      if (caught?.code !== 'auth/popup-closed-by-user') setError(failure ?? caught.message)
    } finally {
      setBusy(false)
    }
  }, [])

  const signIn = () =>
    run(async () => {
      await signInWithGoogle()
      const account = await fetchAccountProfile()
      if (account) {
        planner.adoptAccount(account.profile, account.location)
        lastSaved.current = JSON.stringify({
          profile: { ...planner.profile, ...account.profile },
          location: account.location || planner.location,
        })
        setNotice('Signed in. Your account’s saved details are now on this device.')
      } else {
        if (planner.hasProfile) await saveAccountProfile(planner.profile, planner.location)
        lastSaved.current = JSON.stringify({ profile: planner.profile, location: planner.location })
        setNotice('Signed in. Your details are saved to your account.')
      }
    }, 'Sign-in did not finish. Try again.')

  const signOut = () =>
    run(async () => {
      await signOutUser()
      lastSaved.current = null
      planner.forget()
    }, 'Sign-out did not finish. Try again.')

  const deleteAccount = () =>
    run(async () => {
      try {
        await deleteAccountData()
      } catch {
        throw new Error('Your account could not be deleted, and nothing was removed. Try again.')
      }
      lastSaved.current = null
      planner.forget()
      try {
        await deleteSignIn()
      } catch {
        throw new Error(
          'Your saved plans and details were deleted, but the Google sign-in itself could not be removed. Try again.',
        )
      }
    })

  const value = {
    enabled: accountsEnabled,
    user,
    signedIn,
    busy,
    error,
    notice,
    signIn,
    signOut,
    deleteAccount,
  }
  return <AccountContext.Provider value={value}>{children}</AccountContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAccount() {
  const account = useContext(AccountContext)
  if (!account) throw new Error('useAccount needs an AccountProvider')
  return account
}
