import { Bookmark, History } from './components/icons/glyphs'
import { Route, Routes } from 'react-router-dom'

import AppShell from './app/AppShell'
import CaloriesPage from './pages/CaloriesPage'
import { AccountProvider } from './app/AccountContext'
import { accountsEnabled } from './auth/firebase'
import { PlannerProvider } from './app/PlannerContext'
import HomePage from './pages/HomePage'
import ListPage from './pages/ListPage'
import PlanPage from './pages/PlanPage'
import ProfilePage from './pages/ProfilePage'
import StoredPlanPage from './pages/StoredPlanPage'

// The kitchen app (spec 2026-11-22): home, the plan, saved meals, past plans
// the calorie estimate and the profile. URLs carry a request ID at most, never a health detail.
function App() {
  return (
    <PlannerProvider>
      <AccountProvider>
      <Routes>
        <Route element={<AppShell />}>
          <Route element={<HomePage />} index />
          <Route element={<PlanPage />} path="plan" />
          <Route element={<StoredPlanPage />} path="plans/:requestId" />
          <Route
            element={
              <ListPage
                Icon={Bookmark}
                empty="Meals you save from a plan show up here."
                intro={
                  accountsEnabled
                    ? 'Meals you saved, newest first. Sign in with Google to keep them on any device.'
                    : 'Meals you saved on this device, newest first.'
                }
                pick={(lists) => lists.saved}
                title="My meals"
              />
            }
            path="meals"
          />
          <Route
            element={
              <ListPage
                Icon={History}
                empty="Plans you make show up here."
                intro={
                  accountsEnabled
                    ? 'Every meal you planned, newest first. Sign in with Google to keep them on any device.'
                    : 'Every meal planned on this device, newest first. History lives on the API you are connected to, and it is lost when that server is replaced.'
                }
                pick={(lists) => lists.history}
                title="Past plans"
              />
            }
            path="history"
          />
          <Route element={<CaloriesPage />} path="calories" />
          <Route element={<ProfilePage />} path="profile" />
          <Route element={<HomePage />} path="*" />
        </Route>
      </Routes>
      </AccountProvider>
    </PlannerProvider>
  )
}

export default App
