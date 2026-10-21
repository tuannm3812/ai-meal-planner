import { useState } from 'react'

import { API_BASE_URL } from './api/client'
import BrandBar from './components/brand/BrandBar'
import TabBar from './components/ui/TabBar'
import CaloriesTab from './features/calories/CaloriesTab'
import HistoryTab from './features/history/HistoryTab'
import MealPlanTab from './features/mealPlan/MealPlanTab'

function App() {
  const [activeTab, setActiveTab] = useState('meal')

  return (
    <>
      <BrandBar />
      <main className="min-h-screen bg-ground px-4 py-8 text-ink sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-7">
          <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-accent-text">
                Multi-Agent Meal Planner
              </p>
              <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">
                Meal planning dashboard
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
                Generate a structured meal, verified nutrition macros, and a grocery receipt
                from a single craving, predict calorie expenditure, and review history.
              </p>
            </div>
            <div className="rounded-xl border border-gray-100 bg-white px-4 py-3 text-xs text-gray-500 shadow-sm">
              API target <span className="ml-1 font-medium text-gray-900">{API_BASE_URL}</span>
            </div>
          </header>

          <TabBar activeTab={activeTab} onChange={setActiveTab} />

          {activeTab === 'meal' && <MealPlanTab />}
          {activeTab === 'calories' && <CaloriesTab />}
          {activeTab === 'history' && <HistoryTab />}
        </div>
      </main>
    </>
  )
}

export default App
