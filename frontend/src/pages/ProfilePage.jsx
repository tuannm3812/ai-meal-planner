import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'

import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import { ArrowRight, History, Trash2, UserRound } from '../components/icons/glyphs'
import { card, pageShell, secondaryButton, sideHeading } from '../components/ui/styles'
import AccountSection from '../features/account/AccountSection'
import LocationField from '../features/profile/LocationField'
import ProfileForm from '../features/profile/ProfileForm'
import SizingPanel from '../features/profile/SizingPanel'

// What this device keeps, as three short facts rather than a paragraph.
const DEVICE_FACTS = [
  { glyph: UserRound, title: 'Kept in this browser', text: 'So you don’t retype your details.' },
  { glyph: ArrowRight, title: 'Sent with each plan', text: 'The service needs them to size your meal.' },
  {
    glyph: History,
    title: 'Plan history',
    text: 'When the app runs locally, the server keeps your past plans, including these details.',
  },
]

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
        <ul className="mt-3 flex flex-col gap-3 text-sm leading-5 text-muted">
          {DEVICE_FACTS.map((fact) => (
            <li className="flex items-start gap-3" key={fact.title}>
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-tint">
                <Icon as={fact.glyph} size="sm" tone="light" />
              </span>
              <span>
                <span className="block font-semibold text-ink">{fact.title}</span>
                {fact.text}
              </span>
            </li>
          ))}
        </ul>
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
