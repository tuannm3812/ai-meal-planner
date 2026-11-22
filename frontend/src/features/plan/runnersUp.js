// "Also close to your craving": the retrieval's other ranked meals, never the
// one served. Planning one sends its name as the craving (spec §4.3).
export function runnersUp(plan, max = 3) {
  const retrieval = plan?.meal_plan?.retrieval
  const candidates = Array.isArray(retrieval?.candidates) ? retrieval.candidates : []
  const served = retrieval?.selected_meal_id
  const servedName = plan?.meal_plan?.meal_definition?.structured_meal_name
  return [...candidates]
    .filter((candidate) => candidate?.name && candidate.meal_id !== served && candidate.name !== servedName)
    .sort((a, b) => (a.rank ?? Infinity) - (b.rank ?? Infinity))
    .slice(0, max)
    .map((candidate) => ({ id: candidate.meal_id ?? candidate.name, name: candidate.name }))
}
