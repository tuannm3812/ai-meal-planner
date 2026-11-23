import { useState } from 'react'

import { useAccount } from '../../app/AccountContext'
import Icon from '../../components/icons/Icon'
import { LogIn, LogOut, Trash2 } from '../../components/icons/glyphs'
import { card, primaryButton, secondaryButton, sectionHeading } from '../../components/ui/styles'

// The Profile page's account card (DEC-43): sign in with Google, sign out, or
// delete the account and everything it stored. Shown only with accounts on.
function AccountSection() {
  const account = useAccount()
  const [confirming, setConfirming] = useState(false)

  if (!account.enabled) return null
  const { user, signedIn, busy } = account
  const who = user?.name && user?.email ? `${user.name} (${user.email})` : user?.email || user?.name

  return (
    <section aria-labelledby="account-heading" className={card}>
      <h2 className={sectionHeading} id="account-heading">
        Your account
      </h2>
      {signedIn ? (
        <>
          <p className="mt-2 max-w-3xl text-muted">
            Signed in{who ? ` as ${who}` : ''}. Your details, saved meals and past plans are kept
            in your account, so they follow you to any device. The server keeps only an account ID,
            never your name or email.
          </p>
          {confirming ? (
            <div
              aria-labelledby="delete-question"
              className="mt-4 flex flex-col gap-3 rounded-2xl bg-tint p-4"
              role="alertdialog"
            >
              <p className="font-semibold" id="delete-question">
                Delete your account? This permanently deletes your saved meals, past plans, ratings
                and details, and removes your sign-in.
              </p>
              <div className="flex flex-wrap gap-3">
                <button
                  className={`${secondaryButton} border-accent-text text-accent-text`}
                  disabled={busy}
                  onClick={async () => {
                    await account.deleteAccount()
                    setConfirming(false)
                  }}
                  type="button"
                >
                  Yes, delete everything
                </button>
                <button
                  className={secondaryButton}
                  disabled={busy}
                  onClick={() => setConfirming(false)}
                  type="button"
                >
                  Keep my account
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-4 flex flex-wrap gap-3">
              <button
                className={secondaryButton}
                disabled={busy}
                onClick={account.signOut}
                type="button"
              >
                <Icon as={LogOut} size="sm" />
                Sign out
              </button>
              <button
                className={secondaryButton}
                disabled={busy}
                onClick={() => setConfirming(true)}
                type="button"
              >
                <Icon as={Trash2} size="sm" />
                Delete my account and data
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          <p className="mt-2 max-w-3xl text-muted">
            Sign in with Google to keep your details, saved meals and past plans on any device. Until
            then they are kept for this browser only.
          </p>
          <button className={`${primaryButton} mt-4`} disabled={busy} onClick={account.signIn} type="button">
            <Icon as={LogIn} size="sm" />
            Sign in with Google
          </button>
        </>
      )}
      {account.notice && (
        <p className="mt-3 text-sm" role="status">
          {account.notice}
        </p>
      )}
      {account.error && (
        <p className="mt-3 text-sm text-accent-text" role="alert">
          {account.error}
        </p>
      )}
    </section>
  )
}

export default AccountSection
