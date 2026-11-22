export const formatCurrency = (value) =>
  new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
  }).format(Number(value || 0))

export const formatMacro = (value, unit) => `${Number(value || 0).toFixed(1)}${unit}`

export const formatDateTime = (value) => {
  if (!value) return 'Unknown time'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleString('en-AU', { dateStyle: 'medium', timeStyle: 'short' })
}

export const parseCommaList = (value) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

export const macroCards = [
  { key: 'total_calories', label: 'Calories', unit: ' kcal' },
  { key: 'total_protein', label: 'Protein', unit: 'g' },
  { key: 'total_carbs', label: 'Carbs', unit: 'g' },
  { key: 'total_fat', label: 'Fat', unit: 'g' },
]
