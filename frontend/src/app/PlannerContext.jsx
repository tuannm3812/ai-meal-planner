import { createContext, useContext } from 'react'

import { usePlanner } from './usePlanner'

const PlannerContext = createContext(null)

// One planner for the whole app, so the profile, craving, plan and ticks
// survive moving between pages.
export function PlannerProvider({ children }) {
  const planner = usePlanner()
  return <PlannerContext.Provider value={planner}>{children}</PlannerContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePlannerContext() {
  const planner = useContext(PlannerContext)
  if (!planner) throw new Error('usePlannerContext needs a PlannerProvider')
  return planner
}
