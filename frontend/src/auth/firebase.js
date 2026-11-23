// Signed-in accounts (DEC-43, docs/superpowers/specs/2026-11-22-user-accounts-design.md).
//
// Accounts are on only when the build carries the Firebase web config
// (VITE_FIREBASE_*). That config is public, not a secret: Firebase names the
// project with it, and the project's authorised domains limit where sign-in
// works. Without it the app behaves exactly as before: an ID on this device and
// no Authorization header, which is how it runs against a local API.
//
// With it, every API call carries the signed-in user's ID token. A visitor who
// has not signed in with Google is signed in anonymously, but only when the app
// first calls the API, so a first visit still makes no network call before the
// person plans (DEC-37). Signing in with Google later links that anonymous
// account, so its uid, and the plans stored under it, carry over.
import { initializeApp } from 'firebase/app'
import {
  GoogleAuthProvider,
  deleteUser,
  getAuth,
  linkWithPopup,
  onAuthStateChanged,
  reauthenticateWithPopup,
  signInAnonymously,
  signInWithCredential,
  signInWithPopup,
  signOut,
} from 'firebase/auth'

const env = import.meta.env

export const firebaseConfig = {
  apiKey: env.VITE_FIREBASE_API_KEY,
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: env.VITE_FIREBASE_PROJECT_ID,
  appId: env.VITE_FIREBASE_APP_ID,
}

export const accountsEnabled = Boolean(
  firebaseConfig.apiKey && firebaseConfig.authDomain && firebaseConfig.projectId,
)

let auth = null
function getFirebaseAuth() {
  if (!accountsEnabled) return null
  if (!auth) auth = getAuth(initializeApp(firebaseConfig))
  return auth
}

// What the app shows of a user: never sent to the API, which keeps only the uid.
export function describeUser(user) {
  if (!user) return null
  return {
    uid: user.uid,
    isAnonymous: user.isAnonymous,
    name: user.displayName || null,
    email: user.email || null,
    photoUrl: user.photoURL || null,
  }
}

// Calls `callback` with the described user now and on every change. Returns
// the unsubscribe function; a no-op when accounts are off.
export function watchUser(callback) {
  const current = getFirebaseAuth()
  if (!current) {
    callback(null)
    return () => {}
  }
  return onAuthStateChanged(current, (user) => callback(describeUser(user)))
}

let anonymousSignIn = null
async function ensureUser(current) {
  await current.authStateReady()
  if (current.currentUser) return current.currentUser
  // One sign-in however many calls arrive together.
  anonymousSignIn ??= signInAnonymously(current).finally(() => {
    anonymousSignIn = null
  })
  return (await anonymousSignIn).user
}

// The headers and the uid for one API call: {} and null when accounts are off.
export async function apiIdentity() {
  const current = getFirebaseAuth()
  if (!current) return { headers: {}, uid: null }
  const user = await ensureUser(current)
  const token = await user.getIdToken()
  return { headers: { Authorization: `Bearer ${token}` }, uid: user.uid }
}

// Google sign-in. An anonymous visitor's account is linked, keeping its uid. If
// that Google account already exists, the app signs into it instead and the
// anonymous records stay with the anonymous uid (the spec does not merge them).
export async function signInWithGoogle() {
  const current = getFirebaseAuth()
  const provider = new GoogleAuthProvider()
  await current.authStateReady()
  const user = current.currentUser
  if (user?.isAnonymous) {
    try {
      return describeUser((await linkWithPopup(user, provider)).user)
    } catch (error) {
      const credential = GoogleAuthProvider.credentialFromError(error)
      if (error?.code === 'auth/credential-already-in-use' && credential) {
        return describeUser((await signInWithCredential(current, credential)).user)
      }
      throw error
    }
  }
  return describeUser((await signInWithPopup(current, provider)).user)
}

export async function signOutUser() {
  const current = getFirebaseAuth()
  if (current) await signOut(current)
}

// Deletes the Firebase sign-in itself, after the API has deleted the data.
// Firebase asks for a recent sign-in first, so a stale one signs in again.
export async function deleteSignIn() {
  const current = getFirebaseAuth()
  const user = current?.currentUser
  if (!user) return
  try {
    await deleteUser(user)
  } catch (error) {
    if (error?.code !== 'auth/requires-recent-login') throw error
    await reauthenticateWithPopup(user, new GoogleAuthProvider())
    await deleteUser(user)
  }
}
