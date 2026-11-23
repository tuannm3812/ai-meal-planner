import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import { Trash2 } from '../components/icons/glyphs'
import { card, pageShell, secondaryButton, sideHeading } from '../components/ui/styles'
import AccountSection from '../features/account/AccountSection'
import LocationField from '../features/profile/LocationField'
import ProfileForm from '../features/profile/ProfileForm'
import SizingPanel from '../features/profile/SizingPanel'

// Your details and what this device remembers. The calorie estimate has its
// own Calories tab (DEC-44).
function ProfilePage() {
  const planner = usePlannerContext()
  const navigate = useNavigate()
  const [confirming, setConfirming] = useState(false)

  if (!planner.hasProfile) return <Navigate replace to="/" />

  const forget = () => {
    planner.forget()
    navigate('/')
  }

  return (
    <main className={`${pageShell} grid gap-6 py-8 xl:grid-cols-[minmax(0,1fr)_360px] xl:items-start`}>
      <ProfileForm
        errors={planner.fieldErrors}
        eyebrow="Your profile"
        intro="Every meal is sized from these details. A change applies from your next plan."
        title="Your details"
        onChange={planner.setProfile}
        profile={planner.profile}
        showSizing={false}
      >
        <LocationField
          error={planner.requestFieldErrors.location}
          onChange={planner.setLocation}
          value={planner.location}
        />
      </ProfileForm>

      {/* Beside the form on wide screens: how a meal is sized, the account,
          and what this device keeps. */}
      <div className="flex min-w-0 flex-col gap-6">
      <SizingPanel stacked />
      <AccountSection />

      <section aria-labelledby="device-heading" className={card}>
        <h2 className={sideHeading} id="device-heading">
          Remembered on this device
        </h2>
        <p className="mt-2 max-w-3xl text-muted">
          Your details are kept in this browser so you don&rsquo;t retype them. They go with each
          plan request, and when the app runs locally the server keeps a history of plans,
          including these details.
        </p>
        {!planner.canRemember && (
          <p className="mt-2 text-sm text-accent-text" role="status">
            This browser is blocking storage, so your details last only until you close the page.
          </p>
        )}
        {confirming ? (
          <div className="mt-4 flex flex-col gap-3 rounded-2xl bg-tint p-4" role="alertdialog" aria-labelledby="forget-question">
            <p className="font-semibold" id="forget-question">
              Forget your details on this device? Plans already on the server are not deleted.
            </p>
            <div className="flex flex-wrap gap-3">
              <button className={`${secondaryButton} border-accent-text text-accent-text`} onClick={forget} type="button">
                Yes, forget me
              </button>
              <button className={secondaryButton} onClick={() => setConfirming(false)} type="button">
                Keep my details
              </button>
            </div>
          </div>
        ) : (
          <button className={`${secondaryButton} mt-4`} onClick={() => setConfirming(true)} type="button">
            <Icon as={Trash2} size="sm" />
            Forget me on this device
          </button>
        )}
      </section>
      </div>
    </main>
  )
}

export default ProfilePage
