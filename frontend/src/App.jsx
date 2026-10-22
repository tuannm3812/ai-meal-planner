import { useState } from 'react'

import BrandBar from './components/brand/BrandBar'
import CaloriesTab from './features/calories/CaloriesTab'
import MealFlow from './features/flow/MealFlow'
import HistoryTab from './features/history/HistoryTab'
import { DEFAULT_PROFILE } from './features/profile/profile'

// An opaque ID for this visit, out of sight (docs/8_design.md §3.1). It is in
// the history URL, which access logs record, so it says nothing about anyone.
function newUserId() {
  return `web-${globalThis.crypto.randomUUID()}`
}

const link =
  'min-h-[44px] rounded-lg px-3 text-sm font-medium text-ink underline-offset-4 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ink'

// One guided flow (DEC-29). Past plans and the separate calorie estimate are
// small links, not tabs (§7). The flow stays mounted while they are open, so
// coming back keeps the profile, craving and plan.
function App() {
  const [view, setView] = useState('flow')
  const [profile, setProfile] = useState(DEFAULT_PROFILE)
  const [userId] = useState(newUserId)

  return (
    <>
      <BrandBar>
        <nav aria-label="More" className="flex flex-wrap gap-1">
          <button
            aria-pressed={view === 'history'}
            className={link}
            onClick={() => setView('history')}
            type="button"
          >
            Past plans
          </button>
          <button
            aria-pressed={view === 'calories'}
            className={link}
            onClick={() => setView('calories')}
            type="button"
          >
            Calorie estimate
          </button>
        </nav>
      </BrandBar>

      <main className="min-h-screen bg-ground px-4 py-8 text-ink sm:px-6">
        <div className="mx-auto max-w-6xl">
          <div hidden={view !== 'flow'}>
            <MealFlow onProfileChange={setProfile} profile={profile} userId={userId} />
          </div>

          {view !== 'flow' && (
            <div className="flex flex-col gap-6">
              <div>
                <button
                  className="min-h-[44px] rounded-xl border border-ink px-4 text-sm font-semibold text-ink"
                  onClick={() => setView('flow')}
                  type="button"
                >
                  Back to your meal
                </button>
              </div>
              {view === 'history' && <HistoryTab initialUserId={userId} />}
              {view === 'calories' && <CaloriesTab />}
            </div>
          )}
        </div>
      </main>
    </>
  )
}

export default App
