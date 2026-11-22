// Which flat drawing stands for a meal. It shows a kind of dish, never the
// meal itself (the service has no photos). First keyword wins, so a noodle
// soup is a soup and stir-fried noodles are noodles.
const RULES = [
  ['soup', /\bsoup\b/],
  ['curry', /\b(curry|chili)\b/],
  ['noodles', /\bnoodles?\b/],
  ['pasta', /\bpasta\b/],
  ['taco', /\b(tacos?|burrito|wrap)\b/],
  ['salad', /\bsalad\b/],
  ['eggs', /\b(toast|omelette|frittata|scramble)\b/],
  ['oats', /\boats?\b/],
  ['stirfry', /\bstir fry\b/],
  ['rice', /\brice\b/],
  ['plate', /\b(plate|hash|traybake|wedges|meatballs?)\b/],
]

export const DISH_TYPES = [...RULES.map(([type]) => type), 'bowl']

export function dishType(mealName) {
  const name = String(mealName || '').toLowerCase()
  const rule = RULES.find(([, pattern]) => pattern.test(name))
  return rule ? rule[0] : 'bowl'
}
