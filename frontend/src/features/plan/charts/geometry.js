// The arithmetic behind the plan page's SVG charts, kept apart so it can be
// tested without rendering.

import { MACRO_COLORS, VIRIDIS } from '../../../theme/tokens'

// Viridis, six steps (DESIGN.md §3), from the tokens file. Categorical series
// take them in order.
export { MACRO_COLORS, VIRIDIS }

// How much of the ring to fill: served over target, capped at a full ring.
export function ringFraction(served, target) {
  if (typeof served !== 'number' || typeof target !== 'number' || target <= 0) return null
  return Math.max(0, Math.min(served / target, 1))
}

// Donut arcs for the macro split, drawn with stroke-dasharray on one circle.
// Each segment is { key, length, offset } in the circle's own units.
export function donutSegments(split, radius, keys = ['protein', 'carbs', 'fat']) {
  const circumference = 2 * Math.PI * radius
  const total = keys.reduce((sum, key) => sum + (split?.[key] ?? 0), 0)
  if (!split || total <= 0) return []
  let start = 0
  return keys.map((key) => {
    const length = ((split[key] ?? 0) / total) * circumference
    const segment = { key, length, offset: -start, circumference }
    start += length
    return segment
  })
}

// "Where the calories come from": the ingredients that carry kcal, largest
// first, each with its share and a ramp colour.
export function sourceSegments(items) {
  const withKcal = (items || []).filter((item) => typeof item.kcal === 'number' && item.kcal > 0)
  const total = withKcal.reduce((sum, item) => sum + item.kcal, 0)
  if (total <= 0) return []
  return [...withKcal]
    .sort((a, b) => b.kcal - a.kcal)
    .map((item, index) => ({
      ...item,
      share: (item.kcal / total) * 100,
      color: VIRIDIS[Math.min(index, VIRIDIS.length - 1)],
    }))
}
