import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import { Calculator, Trash2 } from '../components/icons/glyphs'
import { card, pageShell, secondaryButton, sectionHeading } from '../components/ui/styles'
import AccountSection from '../features/account/AccountSection'
import CaloriesTab from '../features/calories/CaloriesTab'
import LocationField from '../features/profile/LocationField'
import ProfileForm from '../features/profile/ProfileForm'

// Your details, what this device remembers, and the separate calorie
// estimate (docs/8_design.md §7 question 7).
function ProfilePage() {
  const planner = usePlannerContext()
  const navigate = useNavigate()
  const [confirming, setConfirming] = useState(false)
  const [showEstimate, setShowEstimate] = useState(false)

  if (!planner.hasProfile) return <Navigate replace to="/" />

  const forget = () => {
    planner.forget()
    navigate('/')
  }

  return (
    <main className={`${pageShell} flex flex-col gap-6 py-8`}>
      <ProfileForm
        errors={planner.fieldErrors}
        eyebrow="Your profile"
        onChange={planner.setProfile}
        profile={planner.profile}
      >
        <LocationField
          error={planner.requestFieldErrors.location}
          onChange={planner.setLocation}
          value={planner.location}
        />
      </ProfileForm>

      <AccountSection />

      <section aria-labelledby="device-heading" className={card}>
        <h2 className={sectionHeading} id="device-heading">
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

      <section aria-labelledby="estimate-heading" className={card}>
        <h2 className={sectionHeading} id="estimate-heading">
          <Icon as={Calculator} size="lg" tone="light" />
          Calorie estimate
        </h2>
        <p className="mt-2 max-w-3xl text-muted">
          Try the calorie model on its own, with any details. Nothing here changes your profile.
        </p>
        {showEstimate ? (
          <div className="mt-5">
            <CaloriesTab />
          </div>
        ) : (
          <button className={`${secondaryButton} mt-4`} onClick={() => setShowEstimate(true)} type="button">
            Open the calorie estimate
          </button>
        )}
      </section>
    </main>
  )
}

export default ProfilePage
