import { formatCurrency } from '../../lib/format'
import { aisles, storeOf, total } from './shopping'

// The shopping list as plain text for the clipboard: store, then each aisle's
// items with prices, then the estimated total.
export function shoppingText(shopping, mealName) {
  const store = storeOf(shopping)
  const lines = []
  if (mealName) lines.push(`Shopping for ${mealName}`)
  if (store) lines.push(store.address ? `${store.name}, ${store.address}` : store.name)
  for (const group of aisles(shopping)) {
    lines.push('', group.name)
    for (const item of group.items) {
      lines.push(item.price === null ? `- ${item.product}` : `- ${item.product}: ${formatCurrency(item.price)}`)
    }
  }
  const sum = total(shopping)
  if (sum !== null) lines.push('', `Estimated total: ${formatCurrency(sum)}`)
  lines.push('Prices are estimates from a local reference list, not live store prices.')
  return lines.join('\n')
}
